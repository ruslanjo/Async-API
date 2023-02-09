import pytest

from tests.functional.settings import test_settings


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
                'body': body,
            }

        return response_obj

    return inner


@pytest.fixture
def make_cache_request(redis_session):
    async def inner(key: str):
        res = await redis_session.get(key)
        return res

    return inner
