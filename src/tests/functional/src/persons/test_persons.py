import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

test_params = [
    ({'query': 'lucas'}, {'status': 200, 'length': 50}),
    ({'query': 'блаблабла'}, {'status': 404, 'length': 1})
    # len is 1 as for not found {'Detail': Persons not found'} returns
]


@pytest.mark.parametrize("query_data, expected", test_params)
@pytest.mark.asyncio
async def test_search(generated_person_data, es_write_data, make_get_request, query_data, expected):
    # 1. Генерируем данные для ES
    str_query = generated_person_data
    # 2. Загружаем данные в ES
    await es_write_data(str_query)
    # # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/persons/search', query_data)
    # 4. Проверяем ответ
    assert response['status'] == expected['status']
    assert len(response['body']) == expected['length']


test_get_all_params = [
    ({'size': 10}, {'status': 200, 'length': 10}),
    ({'size': 0}, {'status': 200, 'length': 0}),
    ({'number': 10}, {'status': 200, 'length': 0})
]


@pytest.mark.parametrize("query_data, expected", test_get_all_params)
@pytest.mark.asyncio
async def test_get_all(generated_person_data, es_write_data, make_get_request, query_data, expected):
    # 1. Генерируем данные для ES
    str_query = generated_person_data
    # 2. Загружаем данные в ES
    await es_write_data(str_query)
    # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/api/v1/persons/', query_data)
    assert len(response['body']) == expected['length']


test_get_by_id_params = [
    ({'query': 'lucas'}, {'status': 200, 'length': 50}),
    ({'query': 'блаблабла'}, {'status': 404, 'length': 1})
    # len is 1 as for not found {'Detail': Person was not found'} returns
]


@pytest.mark.parametrize("query_data, expected", test_get_by_id_params)
@pytest.mark.asyncio
async def test_get_by_id(generated_person_data, es_write_data, make_get_request, query_data, expected):
    # 1. Генерируем данные для ES
    str_query = generated_person_data
    # 2. Загружаем данные в ES
    await es_write_data(str_query)
    # 3. Дёргаем get_all чтобы в дальнейшем обратиться к get_by_id
    endpoint = '/api/v1/persons/'
    all_persons = await make_get_request(endpoint, query_data)
    person_uuid = all_persons['body'][0].get('id')

    suc_response = await make_get_request(endpoint + person_uuid)
    unsuc_response = await make_get_request(endpoint + 'blablblbl')

    assert suc_response['status'] == 200
    assert suc_response['body']['id'] == person_uuid
    assert unsuc_response['status'] == 404


