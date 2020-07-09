import asyncio
import logging

from utils.events import shutdown

loop = asyncio.get_event_loop()


def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")
    logging.info("Shutting down...")
    loop.create_task(shutdown(loop))