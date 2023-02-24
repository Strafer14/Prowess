from os import environ
import redis
import fakeredis


def create_redis_client():
    environment = environ.get('PYTHON_ENV')
    if environment == 'development':
        redis_host = 'localhost'
        redis_port = 6379
        redis_password = None
        return redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)

    elif environment == 'testing':
        return fakeredis.FakeStrictRedis(version=6)

    else:
        redis_host = environ.get('REDIS_HOST')
        redis_port = environ.get('REDIS_PORT', 6379)
        redis_password = environ.get('REDIS_PWD')
        return redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
