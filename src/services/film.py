from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def search_films(self, query: str, _from: int, size: int) -> Optional[list[Film]]:
        try:
            query_body = {
                        "from": _from,
                        "size": size,
                        "query": {
                            "match": {
                                "description": {
                                    "query": '{}'.format(query),
                                    "fuzziness": "auto"
                                }
                            }
                        }
                    }
            films = await self.elastic.search(
                index="movies",
                body=query_body
            )
        except NotFoundError:
            return None
        return [Film(**film['_source']) for film in films['hits']['hits']]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_films(self, _from: int, size: int, sort: list[dict], filter_genre: str) -> Optional[list[Film]]:
        try:
            query_body = {
                "from": _from,
                "size": size,
                "query": {
                    "match": {
                        "genre": "Comedy"
                    },
                },
                "sort": sort,
            }
            films = await self.elastic.search(
                index="movies",
                body=query_body
            )
        except NotFoundError:
            return None
        return [Film(**film['_source']) for film in films['hits']['hits']]


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
