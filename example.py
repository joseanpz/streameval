#!/usr/bin/env python3.7
"""
Notice! This requires:
 - attrs==18.1.0
"""
import asyncio
import functools
import logging
import random
import signal
import string
import uuid

import attr


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

loop = asyncio.get_event_loop()

@attr.s
class PubSubMessage:
    instance_name = attr.ib()
    message_id    = attr.ib(repr=False)
    hostname      = attr.ib(repr=False, init=False)
    restarted     = attr.ib(repr=False, default=False)
    saved         = attr.ib(repr=False, default=False)
    acked         = attr.ib(repr=False, default=False)
    extended_cnt  = attr.ib(repr=False, default=0)

    def __attrs_post_init__(self):
        self.hostname = f"{self.instance_name}.example.net"


async def publish(queue):
    choices = string.ascii_lowercase + string.digits

    while True:
        msg_id = str(uuid.uuid4())
        host_id = "".join(random.choices(choices, k=4))
        instance_name = f"cattle-{host_id}"
        msg = PubSubMessage(message_id=msg_id, instance_name=instance_name)
        # publish an item
        loop.create_task(queue.put(msg))
        logging.info(f"Published message {msg}")
        # simulate randomness of publishing messages
        await asyncio.sleep(random.random())


async def save(msg):
    # unhelpful simulation of i/o work
    await asyncio.sleep(random.random())
    msg.saved = True
    logging.info(f"Saved {msg} into database")


async def restart_host(msg):
    # unhelpful simulation of i/o work
    await asyncio.sleep(random.random())
    msg.restarted = True
    logging.info(f"Restarted {msg.hostname}")


async def cleanup(msg, event):
    # this will block the rest of the coro until `event.set` is called
    await event.wait()
    # unhelpful simulation of i/o work
    await asyncio.sleep(random.random())
    msg.acked = True
    logging.info(f"Done. Acked {msg}")


async def extend(msg, event):
    while not event.is_set():
        msg.extended_cnt += 1
        logging.info(f"Extended deadline by 3 seconds for {msg}")
        # want to sleep for less than the deadline amount
        await asyncio.sleep(2)


async def handle_message(msg):
    event = asyncio.Event()

    loop.create_task(extend(msg, event))
    loop.create_task(cleanup(msg, event))

    await asyncio.gather(save(msg), restart_host(msg))
    event.set()


async def consume(queue):
    while True:
        msg = await queue.get()
        logging.info(f"Consumed {msg}")
        loop.create_task(handle_message(msg))


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logging.info(f"Received exit signal {signal.name}...")
    logging.info("Closing database connections")
    logging.info("Nacking outstanding messages")
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.Task.current_task()]

    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info(f"Flushing metrics")
    loop.stop()


def main():
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: loop.create_task(shutdown(s, loop)))
    try:
        loop.create_task(publish(queue))
        loop.create_task(consume(queue))
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Process interrupted")
    finally:
        loop.close()
        logging.info("Successfully shutdown the Mayhem service.")


if __name__ == "__main__":
    main()
