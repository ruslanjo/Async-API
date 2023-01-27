import json

from aioredis import Redis
import pydantic


class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def put_query_to_cache(self, endpoint: str, query: dict, value: list | str, cache_exp: int) -> list | None:
        if not endpoint:
            return

        if isinstance(value, list):
            value = [model.json() for model in value if isinstance(model, pydantic.BaseModel)]

        query_params_key = self._prepare_query_params(query)

        await self.redis.set(key=f'{endpoint}:{query_params_key}', value=json.dumps(value), expire=cache_exp)

    async def get_query_from_cache(self, endpoint: str, query: dict, model: pydantic.BaseModel
                                   ) -> list[pydantic.BaseModel] | pydantic.BaseModel | None:

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
            query_params.append(f'{k}={v}')

        query_params = sorted(query_params)  # sorting to handle cases when same
        # keys in different queries has different order, so it will produce different cache_keys
        return '_'.join(query_params)
