from functools import lru_cache
from typing import Optional
from uuid import UUID

from fastapi import Depends

from core.config import PERSON_CACHE_EXPIRE_IN_SECONDS
from dao.person_dao import BasePersonDAO, get_person_dao
from models.film import Film
from models.person import Person
from services.cache import Cache, get_cache


class PersonService:
    def __init__(self, cache: Cache = Depends(get_cache), dao: BasePersonDAO = Depends(get_person_dao)):
        self.dao = dao
        self.cache = cache

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self.cache.get_query_from_cache(query={'uuid': person_id}, model=Person)

        if not person:
            person = await self.dao.get_by_id(person_id)

            if not person:
                return None

            await self.cache.put_query_to_cache(query={'uuid': person.id, 'value': person},
                                                cache_exp=PERSON_CACHE_EXPIRE_IN_SECONDS)
        return person

    async def get_all(self, _from: int, page_size: int) -> Optional[list[Person]]:
        res = await self.dao.get_all(_from, page_size)
        return res

    async def get_films_by_person_id(self, person_id: UUID, page_number: int, page_size: int) -> list[Film] | None:
        person_data = await self.get_by_id(person_id)
        if not person_data:
            return None

        film_ids = person_data.film_ids
        films = await self.dao.get_films_by_ids(film_ids, page_number, page_size)
        return films

    async def search_persons_by_name(self, query: str, _from: int, page_size: int):
        query_dict = {
            'endpoint': 'persons/search',
            'query': query,
            'from': _from,
            'page_size': page_size,
        }

        person_data = await self.cache.get_query_from_cache(query_dict, Person)
        if person_data:
            return person_data
        else:
            response_data = await self.dao.search_persons_by_name(query, _from, page_size)

            query_dict['value'] = response_data
            await self.cache.put_query_to_cache(query_dict, PERSON_CACHE_EXPIRE_IN_SECONDS)
            return response_data


@lru_cache()
def get_person_service(
        cache: Cache = Depends(get_cache),
        dao: BasePersonDAO = Depends(get_person_dao),
) -> PersonService:
    return PersonService(cache, dao)
