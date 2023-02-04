import time

from elasticsearch import Elasticsearch

from tests.functional.settings import test_settings

es_host, es_port = test_settings.ELASTIC_HOST, test_settings.ELASTIC_PORT


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{es_host}:{es_port}', validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)

