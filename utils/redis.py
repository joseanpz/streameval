import aioredis

import config


class RedisWrappper:

    def __init__(self, host, port, password, db=0):
        self.url = f'redis://{host}:{port}/{db}'
        self.password = password
        self.redis = None

    async def setup(self):
        try:
            self.redis = await aioredis.create_redis_pool(self.url, password=self.password)
        except Exception as e:
            print('Something happen while connecting to redis!')

    def close(self):
        self.redis.close()


redis_pool = RedisWrappper(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_PASSWORD, config.REDIS_DB)
