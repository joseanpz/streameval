import os


# redis
REDIS_HOST = os.environ.get('REDIS_HOST', None)
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_DB = os.environ.get('REDIS_DB', 0)