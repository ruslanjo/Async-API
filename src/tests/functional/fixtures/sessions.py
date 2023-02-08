import asyncio
import json
import uuid

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch, NotFoundError

from tests.functional.settings import test_settings


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
    redis = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port), minsize=10,
                                             maxsize=20)
    yield redis
    redis.close()
    await redis.wait_closed()
