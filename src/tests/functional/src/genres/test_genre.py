import pytest

test_get_all_params = [
    ({'size': 60}, {'status': 200, 'length': 60}),
]


@pytest.mark.parametrize("query_data, expected", test_get_all_params)
@pytest.mark.asyncio
async def test_get_all(
        prepare_table_for_test,
        make_get_request,
        query_data,
        expected
):
    await prepare_table_for_test('genres')
    response = await make_get_request('/api/v1/genres/', query_data)
    assert len(response['body']) == expected['length']


@pytest.mark.asyncio
async def test_get_by_id(
        prepare_table_for_test,
        make_get_request
):
    await prepare_table_for_test('genres')
    endpoint = '/api/v1/genres/'
    all_genres = await make_get_request(endpoint)
    genre_uuid = all_genres['body'][0].get('id')

    success_response = await make_get_request(endpoint + genre_uuid)
    unsuccess_response = await make_get_request(endpoint + 'blablblbl')

    assert success_response['status'] == 200
    assert success_response['body']['id'] == genre_uuid
    assert unsuccess_response['status'] == 404
