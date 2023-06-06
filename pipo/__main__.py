#!usr/bin/env python3
import os
import time
import signal
import socket
import asyncio
import logging

from pipo.bot import bot, pipo


def add_signal_handlers():
    loop = asyncio.get_event_loop()

    async def shutdown(sig: signal.Signals) -> None:
        """
        Cancel all running async tasks (other than this one) when called.
        By catching asyncio.CancelledError, any running task can perform
        any necessary cleanup when it's cancelled.
        """
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task(loop):
                task.cancel()
                tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("Finished awaiting cancelled tasks, results: {0}".format(results))
        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig)))


def main():
    logging.basicConfig(encoding="utf-8", level=logging.INFO)
    channel = int(os.environ["CHANNEL"])
    voice_channel = int(os.environ["VOICE_CHANNEL"])
    token = os.environ["TOKEN"]

    add_signal_handlers()

    while range(5):  # wait for internet connection
        try:  # TODO remove this check later
            socket.create_connection(("1.1.1.1", 53), timeout=5)
            break
        except OSError:
            logging.getLogger(__name__).error("No internet connection.")
            time.sleep(5)
    pipo.channel_id = channel
    pipo.voice_channel_id = voice_channel
    bot.run(token)


if __name__ == "__main__":
    main()
