import pytest
from elasticsearch import NotFoundError

from tests.functional.settings import test_settings


@pytest.fixture
def delete_table(es_client):
    async def inner(index_name: str):
        try:
            await es_client.indices.delete(index=index_name)
        except NotFoundError:
            pass

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
def prepare_table_for_test(
        es_client,
        delete_table,
        create_table,
        generated_person_data,
        generated_movie_data,
        generated_genre_data
):
    # add new fixture for generated data when ready
    generated_data = {
        'persons': generated_person_data,
        'movies': generated_movie_data,
        'genres': generated_genre_data
    }

    async def inner(index_name: str):
        await delete_table(index_name)
        await create_table(index_name)
        response = await es_client.bulk(generated_data.get(index_name), refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner
