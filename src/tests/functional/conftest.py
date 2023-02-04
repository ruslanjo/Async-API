import aiohttp
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
        es_client.indices.delete(index='persons')
        es_client.indices.create(index='persons',
                                 body={'mappings': schema['es_persons_index'],
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
    async def inner(endpoint: str, query_data):
        session = aiohttp.ClientSession()
        url = f'{test_settings.service_url}{endpoint}{query_data["query"]}'

        async with session.get(url) as response:
            body = await response.json()
            response_obj = {
                'status': response.status,
                'body':  body,
            }

        await session.close()
        return response_obj

    return inner
