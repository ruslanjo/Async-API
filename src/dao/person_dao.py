import abc
from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from dao.base_dao import BaseDAO
from db.elastic import get_elastic
from models.film import Film
from models.person import Person


class BasePersonDAO(BaseDAO):
    @abc.abstractmethod
    async def search_persons_by_name(self, query: str, _from: int, page_size: int):
        pass

    @abc.abstractmethod
    async def get_films_by_ids(self, film_ids: list[str], _from: int, page_size: int
                               ) -> list[Film] | None:
        pass


class PersonElasticDAO(BasePersonDAO):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_all(self, _from: int, page_size: int) -> list[Person] | None:
        try:
            body = {
                'from': _from,
                'page_size': page_size,
                'query': {
                    'match_all': {}}
            }
            res = await self.elastic.search(index='persons', body=body)
            res = res['hits']['hits']
            persons = [Person(**person['_source']) for person in res]

            return persons

        except NotFoundError:
            return None

    async def get_by_id(self, item_id: UUID) -> Person | None:
        try:
            person = await self.elastic.get('persons', item_id)
        except NotFoundError:
            return None
        return Person(**person['_source'])

    async def search_persons_by_name(self, query: str, _from: int, page_size: int):
        body = {
            "from": _from,
            "size": page_size,
            "query": {
                "match": {
                    "full_name": {
                        "query": f"{query}",
                        "auto_generate_synonyms_phrase_query": True,
                        "fuzziness": "auto"
                    }
                }
            }
        }

        person_data = await self.elastic.search(index='persons', body=body)

        if not person_data:
            return None

        person_data = person_data['hits']['hits']
        return [Person(**person['_source']) for person in person_data]

    async def get_films_by_ids(self, film_ids: list[str], _from: int, page_size: int
                               ) -> list[Film] | None:
        body = {
            "from": _from,
            "page_size": page_size,
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


@lru_cache()
def get_person_dao(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonElasticDAO:
    return PersonElasticDAO(elastic)
