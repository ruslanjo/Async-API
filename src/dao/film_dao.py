from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from typing import Optional

from dao.base_dao import BaseDAO
from db.elastic import get_elastic
from models.film import Film


class BaseFilmDAO(BaseDAO):

    async def search_films(
            self,
            _from: int,
            size: int,
            query: str
    ) -> Optional[Film]:
        pass


class FilmElasticDAO(BaseFilmDAO):
    def __init__(
            self,
            elastic: AsyncElasticsearch
    ):
        self.elastic = elastic

    async def get_by_id(
            self,
            film_id: UUID
    ) -> Film | None:

        try:
            doc = await self.elastic.get(
                'movies',
                film_id
            )
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def get_all(
            self,
            _from: int,
            size: int,
            filter_genre: str,
            sort: str
    ) -> list[Film] | None:

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

    async def search_films(
            self,
            _from: int,
            size: int,
            query: str
    ) -> Optional[Film]:

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
        if not films:
            return None
        films = films['hits']['hits']
        return [
            Film(**film['_source']) for film in films
        ]


@lru_cache()
def get_film_dao(
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmElasticDAO:
    return FilmElasticDAO(elastic)
