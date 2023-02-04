import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.conftest import es_write_data, make_get_request

test_params = [
    ({'query': 'lucas'}, {'status': 200, 'length': 50}),
    ({'query': 'блаблабла'}, {'status': 404, 'length': 1})  # len is 1 as for not found {'Detail': Persons not found'} returns
]


@pytest.mark.parametrize("query_data, expected", test_params)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, query_data, expected):
    # 1. Генерируем данные для ES

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

    # 2. Загружаем данные в ES

    await es_write_data(str_query)

    # # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/persons/search?query=', query_data)

    # 4. Проверяем ответ

    assert response['status'] == expected['status']
    assert len(response['body']) == expected['length']
    assert 1 == 1

