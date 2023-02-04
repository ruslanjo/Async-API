import asyncio
import json
import uuid

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}'])
    yield client
    await client.close()


@pytest.fixture
def es_write_data():
    async def inner(bulk_data: list[dict]):
        es_client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}'])
        schema = test_settings.dict()
        await es_client.indices.delete(index='persons')
        await es_client.indices.create(index='persons',
                                       body={
                                           'mappings': schema['es_persons_index'],
                                           'settings': schema['es_persons_index_settings']}
                                       )

        response = await es_client.bulk(bulk_data, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

        await es_client.close()
    return inner


# @pytest.fixture(scope='session')
# async def get_aiohttp_session():
#     session = aiohttp.ClientSession()
#     yield session
#     await session.close()


@pytest.fixture
def make_get_request():
    async def inner(endpoint: str, query_data=None):
        session = aiohttp.ClientSession()
        url = f'{test_settings.service_url}{endpoint}'

        if query_data and isinstance(query_data, dict):
            url += '?'
            for k, v in query_data.items():
                url += f'{str(k)}={str(v)}'

        async with session.get(url) as response:
            body = await response.json()
            response_obj = {
                'status': response.status,
                'body':  body,
            }

        await session.close()
        return response_obj

    return inner


@pytest.fixture
def make_cache_request():
    async def inner(key: str):
        redis = await aioredis.create_redis_pool(('localhost', test_settings.redis_port), minsize=10, maxsize=20)
        res = await redis.get(key)
        redis.close()
        await redis.wait_closed()
        return res
    return inner




@pytest.fixture
def generated_person_data():
    es_data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'George Lucas',
        'roles': ['actor', 'director', 'writer'],
        'film_ids': ["025c58cd-1b7e-43be-9ffb-8571a613579b",
                     "0312ed51-8833-413f-bff5-0e139c11264a",
                     "0659e0e6-504e-4482-8aa9-f7530f36cae2"]
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': 'persons', '_id': row[test_settings.es_id_field]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'
    return str_query

#
# async def foo():
#     redis =  await aioredis.create_redis_pool(('localhost', test_settings.redis_port), minsize=10, maxsize=20)
#     #redis = aioredis.Redis(pool)
#     await redis.set(key='as', value='fdsf')
#     v = await redis.get('asfds')
#     print(v)
#     redis.close()
#
#
# asyncio.run(foo())