from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import ELASTIC_REQUEST_SIZE
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)

            if not person:
                return None

            await self._put_person_to_redis(person)

        return person

    async def get_all(self) -> Optional[list[Person]]:
        try:
            body = {
                'size': ELASTIC_REQUEST_SIZE,
                'query': {
                    'match_all': {}}
            }
            res = await self.elastic.search(index='persons', body=body)
            res = res['hits']['hits']
            persons = [Person(**person['_source']) for person in res]

            return persons

        #search after - from pagination

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

    async def _get_films_by_ids_from_elastic(self, film_ids: list[str]) -> list[Film] | None:
        body = {
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

    async def get_films_by_person_id(self, person_id: str) -> list[Film] | None:
        person_data = await self.get_by_id(person_id)
        if not person_data:
            return None

        film_ids = person_data.film_ids
        films = await self._get_films_by_ids_from_elastic(film_ids)
        return films


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
