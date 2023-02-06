from functools import lru_cache
from typing import Optional

from fastapi import Depends

from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from models.film import Film
from services.cache import Cache, get_cache
from dao.film_dao import BaseFilmDAO, get_film_dao


class FilmService:
    def __init__(self, cache: Cache = Depends(get_cache), dao: BaseFilmDAO = Depends(get_film_dao)):
        self.dao = dao
        self.cache = cache

    async def get_by_id(
            self,
            film_id: str
    ) -> Optional[Film]:

        film = await self.cache.get_query_from_cache(query={'uuid': film_id}, model=Film)
        if not film:
            film = await self.dao.get_by_id(film_id)
            if not film:
                return None
            await self.cache.put_query_to_cache(query={'uuid': film.id, 'value': film},
                                                cache_exp=FILM_CACHE_EXPIRE_IN_SECONDS)
        return film

    async def search_films(
            self,
            query: str,
            _from: int,
            size: int
    ) -> Optional[list[Film]]:

        query_dict = {
            'endpoint': 'films/search',
            'query': query,
            'from': _from,
            'page_size': size
        }
        film_data = await self.cache.get_query_from_cache(query_dict, Film)
        if film_data:
            return film_data
        else:
            films = await self.dao.search_films(_from, size, query)
            if not films:
                return None

            query_dict['value'] = films
            await self.cache.put_query_to_cache(
                query_dict,
                FILM_CACHE_EXPIRE_IN_SECONDS
            )
            return films

    async def get_films(
            self, _from: int,
            size: int,
            sort: list[dict],
            filter_genre: str
    ) -> Optional[list[Film]]:
        return await self.dao.get_all(
            _from,
            size,
            filter_genre,
            sort
        )


@lru_cache()
def get_film_service(
        cache: Cache = Depends(get_cache),
        dao: BaseFilmDAO = Depends(get_film_dao),
) -> FilmService:
    return FilmService(cache, dao)
