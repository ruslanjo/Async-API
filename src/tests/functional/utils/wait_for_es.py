import time

from elasticsearch import Elasticsearch

from tests.functional.settings import test_settings

es_host, es_port = test_settings.es_host, test_settings.es_port


if __name__ == '__main__':
    print('pinging_es')
    es_client = Elasticsearch(hosts=f'{es_host}:{es_port}', validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        print(f'No connection to es {test_settings.es_host}:{test_settings.es_port}, waiting')
        time.sleep(1)

