import json

import pytest

test_get_all_params = [
    ({'size': 10}, {'status': 200, 'length': 10}),
    ({'size': 50}, {'status': 200, 'length': 50}),
    ({'size': 1}, {'status': 200, 'length': 1}),
]

test_search_params = [
    ({'query': 'Star'}, {'status': 200, 'length': 50}),
    ({'query': 'блаблабла'}, {'status': 404, 'length': 1})
]


@pytest.mark.parametrize("query_data, expected", test_get_all_params)
@pytest.mark.asyncio
async def test_get_all(
        prepare_table_for_test,
        make_get_request,
        query_data,
        expected
):
    await prepare_table_for_test('movies')
    response = await make_get_request('/api/v1/films/', query_data)
    assert len(response['body']) == expected['length']


@pytest.mark.asyncio
async def test_get_by_id(
        prepare_table_for_test,
        make_get_request
):
    await prepare_table_for_test('movies')
    endpoint = '/api/v1/films/'
    all_films = await make_get_request(endpoint)
    film_uuid = all_films['body'][0].get('id')

    success_response = await make_get_request(endpoint + film_uuid)
    unsuccess_response = await make_get_request(endpoint + 'blablblbl')

    assert success_response['status'] == 200
    assert success_response['body']['id'] == film_uuid
    assert unsuccess_response['status'] == 404


@pytest.mark.asyncio
async def test_get_by_id_from_cache(
        prepare_table_for_test,
        make_get_request,
        make_cache_request
):
    await prepare_table_for_test('movies')
    endpoint = '/api/v1/films/'
    all_films = await make_get_request(endpoint)
    film_uuid = all_films['body'][0].get('id')

    suc_response = await make_get_request(endpoint + film_uuid)

    if suc_response['status'] != 200:
        raise AssertionError('no id returned from server')

    cache_data = await make_cache_request(film_uuid)
    assert json.loads(cache_data).get('id') == film_uuid


@pytest.mark.parametrize("query_data, expected", test_search_params)
@pytest.mark.asyncio
async def test_search(prepare_table_for_test, make_get_request, query_data, expected):
    await prepare_table_for_test('movies')
    response = await make_get_request('/api/v1/films/search/', query_data)
    assert response['status'] == expected['status']
    assert len(response['body']) == expected['length']
