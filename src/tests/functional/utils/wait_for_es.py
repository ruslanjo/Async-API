import time

from elasticsearch import Elasticsearch

from tests.functional.settings import test_settings
from external_connection import backoff
es_host, es_port = test_settings.es_host, test_settings.es_port


@backoff()
def ping_es():
    print('pinging_es')
    es_client = Elasticsearch(hosts=f'{es_host}:{es_port}', validate_cert=False, use_ssl=False)
    es_client.ping()


if __name__ == '__main__':
    ping_es()
