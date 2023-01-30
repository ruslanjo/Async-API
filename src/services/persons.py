from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import PERSON_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from dao.person_dao import BasePersonDAO, get_person_dao
from models.film import Film
from models.person import Person
from services.cache import RedisCache


class PersonService:
    def __init__(self, redis: Redis, dao: BasePersonDAO = Depends(get_person_dao)):
        self.redis = redis
        self.dao = dao
        self.cache = RedisCache(redis)

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self._get_person_from_cache(person_id)

        if not person:
            person = await self.dao.get_by_id(person_id)

            if not person:
                return None

            await self._put_person_to_redis(person)

        return person

    async def get_all(self, _from: int, page_size: int) -> Optional[list[Person]]:
        res = await self.dao.get_all(_from, page_size)
        return res

    async def _get_person_from_cache(self, person_id: UUID):
        person_data = await self.redis.get(person_id)

        if not person_data:
            return None

        person = Person.parse_raw(person_data)
        return person

    async def _put_person_to_redis(self, person: Person):
        await self.redis.set(key=person.id, value=person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_films_by_person_id(self, person_id: UUID, page_number: int, page_size: int) -> list[Film] | None:
        person_data = await self.get_by_id(person_id)
        if not person_data:
            return None

        film_ids = person_data.film_ids
        films = await self.dao.get_films_by_ids(film_ids, page_number, page_size)
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
            response_data = await self.dao.search_persons_by_name(query, _from, page_size)

            await self.cache.put_query_to_cache(endpoint, query_dict, response_data, PERSON_CACHE_EXPIRE_IN_SECONDS)
            return response_data


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        dao: BasePersonDAO = Depends(get_person_dao),
) -> PersonService:
    return PersonService(redis, dao)
