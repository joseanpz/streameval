import asyncio
import logging

from utils.exceptions import CustomException


async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logging.info(f"Received exit signal {signal.name}...")
    logging.info("Closing database connections")
    logging.info("Nacking outstanding messages")
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.Task.current_task()]

    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, CustomException):
            logging.error(f"Custom error: {result}")
        elif isinstance(result, Exception):
            logging.error(f"Handling general error: {result}")

    logging.info(f"Flushing metrics")
    loop.stop()