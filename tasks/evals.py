import asyncio
import logging

import aioredis

import config
from utils.exceptions import CustomException


logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


async def evaluate_model(stream_name: str, latest_id: str = '$'):
    subscriber = await aioredis.create_redis(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}',
        password=config.REDIS_PASSWORD
    )
    data_send = {}
    try:
        while True:
            data = await subscriber.xread([f"{stream_name}:input"], latest_ids=[latest_id])

            if data is None:
                break

            for dt in data:
                latest_id = dt[1].decode("utf-8")
                data_send.update({
                    k.decode("utf-8"): v.decode("utf-8") for k, v in dt[2].items()
                })
                subscriber.xadd(f"{stream_name}:output", data_send)
                logger.info(f"Evaluate input and produce output: {data_send}")
    except asyncio.CancelledError:
        logger.info(f'The evaluation task {stream_name} was cancelled')
    except Exception as e:
        logger.error(f'There was an error in task {stream_name}: {e}')
    finally:
        subscriber.close()
        raise CustomException('test de escepcion!')
        logger.info('finally block for evaluate_model!')
