import asyncio
import logging
import signal

import uvloop

from utils.events import shutdown
from utils.handlers import handle_exception
from tasks.evals import evaluate_model


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s,%(msecs)d %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)  # (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: loop.create_task(shutdown(loop, s)))
    loop.set_exception_handler(handle_exception)

    try:
        # before startup

        # service
        loop.create_task(evaluate_model('test'))

        # running up
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Process interrupted')
    finally:
        # redis_pool.close()
        loop.close()
        logging.info('Succesfully shutdown!')




