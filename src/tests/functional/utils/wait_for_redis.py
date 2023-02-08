import time

from redis import Redis, ConnectionError

from tests.functional.settings import test_settings
from .external_connection import backoff


@backoff()
def ping_redis():
    print('pinging redis')
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port, socket_connect_timeout=1)
    redis.ping()


if __name__ == '__main__':
    ping_redis()
