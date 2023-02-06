# import datetime
# import uuid
# import json
#
# import aiohttp
# import pytest
#
# from elasticsearch import AsyncElasticsearch
#
# from tests.functional.settings import test_settings
#
#
# @pytest.mark.asyncio
# async def test_search():
#     # 1. Генерируем данные для ES
#
    # es_data = [{
    #     'id': str(uuid.uuid4()),
    #     'imdb_rating': 8.5,
    #     'genre': ['Action', 'Sci-Fi'],
    #     'title': 'The Star',
    #     'description': 'New World',
    #     'director': ['Stan'],
    #     'actors_names': ['Ann', 'Bob'],
    #     'writers_names': ['Ben', 'Howard'],
    #     'actors': [
    #         {'id': '111', 'name': 'Ann'},
    #         {'id': '222', 'name': 'Bob'}
    #     ],
    #     'writers': [
    #         {'id': '333', 'name': 'Ben'},
    #         {'id': '444', 'name': 'Howard'}
    #     ]
    # } for _ in range(60)]
    #
    # bulk_query = []
    # for row in es_data:
    #     bulk_query.extend([
    #         json.dumps({'index': {'_index': 'movies', '_id': row[test_settings.es_id_field]}}),
    #         json.dumps(row)
    #     ])
    #
    # str_query = '\n'.join(bulk_query) + '\n'
#
#     # 2. Загружаем данные в ES
#
#     es_client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}'],
#                                    validate_cert=False,
#                                    use_ssl=False)
#     schema = test_settings.dict()
#     # es_client.indices.create(index='movies',
#     #                                body={'mappings': schema['es_movies_index'],
#     #                                'settings': schema['es_movies_index_settings']}
#     #                                )
#
#     response = await es_client.bulk(str_query, refresh=True)
#     await es_client.close()
#     if response['errors']:
#         raise Exception('Ошибка записи данных в Elasticsearch')
#     #
#     # # 3. Запрашиваем данные из ES по API
#     #
#     session = aiohttp.ClientSession()
#     url = test_settings.service_url + '/api/v1/films/search'
#     query_data = {'search': 'The Star'}
#     async with session.get(url, params=query_data) as response:
#         body = await response.json()
#         headers = response.headers
#         status = response.status
#     await session.close()
#
#     # 4. Проверяем ответ
#
#     assert status == 200
#     assert len(body) == 50
#     assert 1 == 1
