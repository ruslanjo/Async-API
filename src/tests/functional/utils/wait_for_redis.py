import time

from redis import Redis, ConnectionError

from tests.functional.settings import test_settings

redis = Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT, socket_connect_timeout=1)

while True:
    try:
        redis.ping()
    except (ConnectionRefusedError, ConnectionError):
        time.sleep(1)
    else:
        break

