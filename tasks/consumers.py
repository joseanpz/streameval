import asyncio
import logging

import aioredis

import config


logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


async def consume_output(stream_name: str, latest_id: str = '$'):
    subscriber = await aioredis.create_redis(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}',
        password=config.REDIS_PASSWORD
    )
    try:
        while True:
            data = await subscriber.xread([f"{stream_name}:output"], latest_ids=[latest_id])
            if data is None:
                break
            for dt in data:
                latest_id = dt[1].decode("utf-8")
                logger.info(dt)
    except asyncio.CancelledError:
        logger.info(f'The consumer task {stream_name} was cancelled')
    except Exception as e:
        logger.error(f'There was an error in task {stream_name}: {e}')
    finally:
        subscriber.close()
        logger.info('finally block for consume_output!')