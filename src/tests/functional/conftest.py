import asyncio
import json
import uuid

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


####################### DUMMY DATA #######################

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


####################### SESSION OBJECTS #######################

@pytest.fixture(scope='session')
async def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}'])
    yield client
    await client.close()


@pytest.fixture(scope='session', autouse=True)
async def aiohttp_session():
    session = aiohttp.ClientSession(trust_env=True)
    yield session
    await session.close()


@pytest.fixture(scope='session', autouse=True)
async def redis_session():
    redis = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port), minsize=10, maxsize=20)
    yield redis
    redis.close()
    await redis.wait_closed()

####################### PRE/POST TEST FIXTURES #######################

@pytest.fixture
def delete_table(es_client):
    async def inner(index_name: str):
        await es_client.indices.delete(index=index_name)
    return inner


@pytest.fixture
def create_table(es_client):
    async def inner(index_name: str):
        schema = test_settings.dict()

        mapping = schema.get(f'es_{index_name}_index')
        settings = schema.get(f'es_{index_name}_index_settings')

        await es_client.indices.create(index=index_name,
                                       body={'mappings': mapping,
                                             'settings': settings}
                                       )
    return inner


@pytest.fixture
def prepare_table_for_test(es_client, delete_table, create_table, generated_person_data):
    # add new fixture for generated data when ready
    generated_data = {
        'persons': generated_person_data,
    }

    async def inner(index_name: str):
        await delete_table(index_name)
        await create_table(index_name)
        response = await es_client.bulk(generated_data.get(index_name), refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def make_get_request(aiohttp_session):
    async def inner(endpoint: str, query_data=None):
        url = f'{test_settings.service_url}{endpoint}'

        if query_data and isinstance(query_data, dict):
            url += '?'
            for k, v in query_data.items():
                url += f'{str(k)}={str(v)}'

        async with aiohttp_session.get(url, ssl=False) as response:
            body = await response.json()
            response_obj = {
                'status': response.status,
                'body':  body,
            }

        return response_obj
    return inner


@pytest.fixture
def make_cache_request(redis_session):
    async def inner(key: str):
        res = await redis_session.get(key)
        return res
    return inner
