from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import PERSON_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person
from services.cache import RedisCache


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.cache = RedisCache(redis)

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)

            if not person:
                return None

            await self._put_person_to_redis(person)

        return person

    async def get_all(self, _from: int, page_size: int) -> Optional[list[Person]]:
        try:
            body = {
                'from': _from,
                'page_size': page_size,
                'query': {
                    'match_all': {}}
            }
            res = await self.elastic.search(index='persons', body=body)
            res = res['hits']['hits']
            persons = [Person(**person['_source']) for person in res]

            return persons

        except NotFoundError:
            return None

    async def _get_person_from_elastic(self, person_id: str):
        try:
            person = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None
        return Person(**person['_source'])

    async def _get_person_from_cache(self, person_id: str):
        person_data = await self.redis.get(person_id)

        if not person_data:
            return None

        person = Person.parse_raw(person_data)
        return person

    async def _put_person_to_redis(self, person: Person):
        await self.redis.set(key=person.id, value=person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _get_films_by_ids_from_elastic(self, film_ids: list[str],
                                             _from: int,
                                             page_size: int) -> list[Film] | None:
        body = {
            "from": _from,
            "page_size": page_size,
            "query": {
                "terms": {
                    "id": film_ids,
                    "boost": 1.0
                }
            }
        }
        matched_films = await self.elastic.search(index='movies', body=body)
        if not matched_films:
            return None
        matched_films = matched_films['hits']['hits']

        return [Film(**film['_source']) for film in matched_films]

    async def get_films_by_person_id(self, person_id: str, page_number: int, page_size: int) -> list[Film] | None:
        person_data = await self.get_by_id(person_id)
        if not person_data:
            return None

        film_ids = person_data.film_ids
        films = await self._get_films_by_ids_from_elastic(film_ids, page_number, page_size)
        return films

    async def search_persons_by_name(self, query: str, _from: int, page_size: int):
        endpoint = 'persons/search'

        query_dict = {
            'query': query,
            'from': _from,
            'page_size': page_size
        }

        person_data = await self.cache.get_query_from_cache(endpoint, query_dict, Person)
        if person_data:
            return person_data
        else:

            body = {
                "from": _from,
                "size": page_size,
                "query": {
                    "match": {
                        "full_name": {
                            "query": f"{query}",
                            "auto_generate_synonyms_phrase_query": True,
                            "fuzziness": "auto"
                        }
                    }
                }
            }

            person_data = await self.elastic.search(index='persons', body=body)

            if not person_data:
                return None

            person_data = person_data['hits']['hits']

            response_data = [Person(**person['_source']) for person in person_data]

            await self.cache.put_query_to_cache(endpoint, query_dict, response_data, PERSON_CACHE_EXPIRE_IN_SECONDS)
            return response_data


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
