from functools import lru_cache
from typing import Optional

from fastapi import Depends

from core.config import GENRE_CACHE_EXPIRE_IN_SECONDS
from models.genre import Genre
from services.cache import Cache, get_cache
from dao.genre_dao import BaseGenreDAO, get_genre_dao


class GenreService:
    def __init__(
            self,
            cache: Cache = Depends(get_cache),
            dao: BaseGenreDAO = Depends(get_genre_dao)
    ):
        self.dao = dao
        self.cache = cache

    async def get_by_id(
            self,
            genre_id: str
    ) -> Optional[Genre]:

        genre = await self.cache.get_query_from_cache(query={'uuid': genre_id}, model=Genre)
        if not genre:
            genre = await self.dao.get_by_id(genre_id)
            if not genre:
                return None
            await self.cache.put_query_to_cache(query={'uuid': genre.id, 'value': genre},
                                                cache_exp=GENRE_CACHE_EXPIRE_IN_SECONDS)
        return genre

    async def get_all(
            self
    ) -> Optional[list[Genre]]:

        return await self.dao.get_all()


@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_cache),
        dao: BaseGenreDAO = Depends(get_genre_dao),
) -> GenreService:

    return GenreService(cache, dao)
