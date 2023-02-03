from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from dao.base_dao import BaseDAO
from db.elastic import get_elastic
from models.genre import Genre


class BaseGenreDAO(BaseDAO):
    pass


class GenreElasticDAO(BaseGenreDAO):
    def __init__(
            self,
            elastic: AsyncElasticsearch
    ):
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def get_all(
            self,
    ) -> list[Genre] | None:
        try:
            docs = await self.elastic.search(
                index='genres',
                body={
                    'query': {
                        'match_all': {}
                    }
                }
            )
            genre_docs = docs['hits']['hits']
            return [Genre(**doc['_source']) for doc in genre_docs]

        except NotFoundError:
            return None


@lru_cache()
def get_genre_dao(
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreElasticDAO:
    return GenreElasticDAO(elastic)
