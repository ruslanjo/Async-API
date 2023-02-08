import time
from functools import wraps

import redis
from elasticsearch import ConnectionError as esConnectionError


connections_errors = (redis.ConnectionError, esConnectionError, ConnectionRefusedError)

def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
       Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
       Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)
       Формула:
           t = start_sleep_time * 2^(n) if t < border_sleep_time
           t = border_sleep_time if t >= border_sleep_time
       :param start_sleep_time: начальное время повтора
       :param factor: во сколько раз нужно увеличить время ожидания
       :param border_sleep_time: граничное время ожидания
       :return: результат выполнения функции
       """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            is_succeeded = False
            num_of_attempts = 0

            while not is_succeeded:

                try:
                    res = func(*args, **kwargs)
                    is_succeeded = True
                    return res

                except connections_errors:

                    sleep_time_calc = start_sleep_time * (factor ** num_of_attempts)
                    sleep_time = sleep_time_calc if sleep_time_calc < border_sleep_time else border_sleep_time

                    num_of_attempts += 1
                    time.sleep(sleep_time)
        return inner
    return func_wrapper
