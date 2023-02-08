import pytest
import json
import uuid

from tests.functional.settings import test_settings


####################### DUMMY DATA #######################
@pytest.fixture
def generated_genre_data():
    es_data = [{
        'id': str(uuid.uuid4()),
        'name': 'Action',
        'description': 'desc',
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': 'genres', '_id': row[test_settings.es_id_field]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    return str_query


@pytest.fixture
def generated_movie_data():
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ]
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': 'movies', '_id': row[test_settings.es_id_field]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    return str_query


@pytest.fixture
def generated_person_data():
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
    return str_query
