from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.cache import RedisCache
from dao.film_dao import BaseFilmDAO, get_film_dao


class FilmService:
    def __init__(
            self,
            redis: Redis,
            dao: BaseFilmDAO = Depends(get_film_dao)
    ):
        self.redis = redis
        self.dao = dao
        self.cache = RedisCache(redis)

    async def get_by_id(
            self,
            film_id: str
    ) -> Optional[Film]:

        film = await self._film_from_cache(film_id)
        if not film:
            film = await self.dao.get_by_id(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def search_films(
            self,
            query: str,
            _from: int,
            size: int
    ) -> Optional[list[Film]]:

        endpoint = 'films/search'
        query_dict = {
            'query': query,
            'from': _from,
            'page_size': size
        }
        film_data = await self.cache.get_query_from_cache(
            endpoint,
            query_dict,
            Film
        )
        if film_data:
            return film_data
        else:
            films = await self.dao.search_films(_from, size, query)
            if not films:
                return None

            await self.cache.put_query_to_cache(
                endpoint,
                query_dict,
                films,
                FILM_CACHE_EXPIRE_IN_SECONDS
            )
            return films

    async def _film_from_cache(
            self,
            film_id: str
    ) -> Optional[Film]:

        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(
            self,
            film: Film
    ):
        await self.redis.set(
            film.id,
            film.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_films(self, _from: int, size: int, sort: list[dict], filter_genre: str) -> Optional[list[Film]]:
        return await self.dao.get_all(
            _from,
            size,
            filter_genre,
            sort
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        dao: BaseFilmDAO = Depends(get_film_dao),
) -> FilmService:
    return FilmService(redis, dao)
