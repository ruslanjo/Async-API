from functools import lru_cache
from typing import Optional

from aioredis import Redis
from fastapi import Depends

from core.config import GENRE_CACHE_EXPIRE_IN_SECONDS
from db.redis import get_redis
from models.genre import Genre
from services.cache import RedisCache
from dao.genre_dao import BaseGenreDAO, get_genre_dao


class GenreService:
    def __init__(
            self,
            redis: Redis,
            dao: BaseGenreDAO = Depends(get_genre_dao)
    ):
        self.redis = redis
        self.dao = dao
        self.cache = RedisCache(redis)

    async def get_by_id(
            self,
            genre_id: str
    ) -> Optional[Genre]:

        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self.dao.get_by_id(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def get_all(
            self
    ) -> Optional[list[Genre]]:

        return await self.dao.get_all()

    async def _genre_from_cache(
            self,
            genre_id: str
    ) -> Optional[Genre]:

        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(
            self, genre: Genre
    ):

        await self.redis.set(
            genre.id, genre.json(),
            expire=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        dao: BaseGenreDAO = Depends(get_genre_dao),
) -> GenreService:

    return GenreService(redis, dao)
