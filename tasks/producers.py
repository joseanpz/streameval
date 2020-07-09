import asyncio
import logging

import aioredis

import config

logger = logging.getLogger(__name__)


async def produce_input(stream_name: str, n: int):
    subscriber = await aioredis.create_redis(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}',
        password=config.REDIS_PASSWORD
    )
    data_send = {'data': ''}
    try:
        for i in range(n):
            data_send['data'] = i
            ret = subscriber.xadd(f"{stream_name}:input", data_send)
            logger.info(f"Produced input: {ret}, {data_send}")
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(e)
    finally:
        subscriber.close()
        logger.info('finally block for produce_input!')