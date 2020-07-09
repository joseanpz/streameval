import asyncio
import logging
import signal

from utils.redis import redis_pool
from utils.events import shutdown
from utils.handlers import handle_exception
from tasks.consumers import consume_output


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s,%(msecs)d %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: loop.create_task(shutdown(loop, s)))
    loop.set_exception_handler(handle_exception)

    try:
        # startup

        # service
        loop.create_task(consume_output('test'))

        # running up
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Process interrupted')
    finally:
        # redis_pool.close()
        loop.close()
        logging.info('Succesfully shutdown!')




