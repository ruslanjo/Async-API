import os

from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_URL')

    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field(6379, env='REDIS_PORT')

    es_host: str = Field('http://127.0.0.1', env='ELASTIC_HOST')
    es_port: str = Field(9200, env='ELASTIC_PORT')
    es_id_field: str = 'id'

    es_movies_index: dict = {
        'dynamic': 'strict',
        'properties': {
            'id': {
                'type': 'keyword'
            },
            'imdb_rating': {
                'type': 'float'
            },
            'genre': {
                'type': 'keyword'
            },
            'title': {
                'type': 'text',
                'analyzer': 'ru_en',
                'fields': {
                    'raw': {
                        'type': 'keyword'
                    }
                }
            },
            'description': {
                'type': 'text',
                'analyzer': 'ru_en'
            },
            'director': {
                'type': 'text',
                'analyzer': 'ru_en'
            },
            'actors_names': {
                'type': 'text',
                'analyzer': 'ru_en'
            },
            'writers_names': {
                'type': 'text',
                'analyzer': 'ru_en'
            },
            'actors': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword'
                    },
                    'name': {
                        'type': 'text',
                        'analyzer': 'ru_en'
                    }
                }
            },
            'writers': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword'
                    },
                    'name': {
                        'type': 'text',
                        'analyzer': 'ru_en'
                    }
                }
            }
        },
    }
    es_movies_index_settings: dict = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    }
    es_genres_index: dict = {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "keyword"
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            }
        }
    }

    es_genres_index_settings: dict = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    }

    es_persons_index: dict = {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "full_name": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "roles": {
                "type": "keyword"
            },
            "film_ids": {
                "type": "keyword"
            }
        }
    }

    es_persons_index_settings: dict = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    }

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_file = '../../.environments.stage/.env.async_api.stage'


test_settings = TestSettings()
