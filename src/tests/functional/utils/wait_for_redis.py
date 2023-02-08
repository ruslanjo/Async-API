import time

from redis import Redis, ConnectionError

from tests.functional.settings import test_settings

redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port, socket_connect_timeout=1)

while True:
    try:
        redis.ping()
    except (ConnectionRefusedError, ConnectionError):
        print(f'No connection to redis {test_settings.redis_host}:{test_settings.redis_port}, waiting')
        time.sleep(1)
    else:
        break

