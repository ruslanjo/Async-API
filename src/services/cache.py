import abc
from abc import ABC
import json
from functools import lru_cache

from aioredis import Redis
import pydantic
from fastapi import Depends

from db.redis import get_redis


class Cache(ABC):
    @abc.abstractmethod
    async def put_query_to_cache(self, query: dict, cache_exp: int) -> None:
        pass

    @abc.abstractmethod
    async def get_query_from_cache(self, query: dict, model: pydantic.BaseModel
                                   ) -> list[pydantic.BaseModel] | pydantic.BaseModel | None:
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def put_query_to_cache(self, query: dict, cache_exp: int) -> None:
        uuid, value = query.get('uuid'), query.get('value')
        if uuid and value:
            await self.redis.set(key=uuid, value=query.get('value').json())
            return

        endpoint = query.get('endpoint')
        if not endpoint:
            return None

        if isinstance(value, list):
            value = [model.json() for model in value if isinstance(model, pydantic.BaseModel)]

        query_params_key = self._prepare_query_params(query)

        await self.redis.set(key=f'{endpoint}:{query_params_key}', value=json.dumps(value), expire=cache_exp)

    async def get_query_from_cache(self, query: dict, model: pydantic.BaseModel
                                   ) -> list[pydantic.BaseModel] | pydantic.BaseModel | None:

        uuid = query.get('uuid')
        if uuid:
            data = await self.redis.get(uuid)
            if not data:
                return None
            return model.parse_raw(data)

        endpoint = query.get('endpoint')
        if not endpoint:
            return None

        query_params_key = self._prepare_query_params(query)
        data = await self.redis.get(f'{endpoint}:{query_params_key}')

        if not data:
            return None

        data = json.loads(data)

        if isinstance(data, list):
            return [model.parse_raw(element) for element in data]
        return model.parse_raw(data)

    def _prepare_query_params(self, query: dict):
        query_params = []
        for k, v in query.items():
            if k in ('endpoint', 'uuid', 'value'):
                continue
            query_params.append(f'{k}={v}')

        query_params = sorted(query_params)  # sorting to handle cases when same
        # keys in different queries has different order, so it will produce different cache_keys
        return '_'.join(query_params)


@lru_cache()
def get_cache(redis: Redis = Depends(get_redis)):
    return RedisCache(redis)
