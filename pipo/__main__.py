#!usr/bin/env python3
import asyncio
import logging
import signal

from pipo.bot import PipoBot
from pipo.cogs import MusicBot
from pipo.config import settings


def add_signal_handlers(loop: asyncio.AbstractEventLoop):
    """Add signal handlers to manage program execution."""

    async def shutdown(sig: signal.Signals, loop: asyncio.AbstractEventLoop) -> None:
        """Cancel all running async tasks.

        Defines shutdown sig catchers for asyncio.CancelledError,
        so that any running task can perform necessary cleanup when it's cancelled.

        Parameters
        ----------
        sig : signal.Signals
            Signal TODO
        """
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task(loop):
                task.cancel()
                tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        loop.add_signal_handler(
            sig,
            lambda x: asyncio.create_task(shutdown(x, loop))
        )


async def main():

    channel = settings.channel
    voice_channel = settings.voice_channel
    token = settings.token

    add_signal_handlers(asyncio.get_event_loop())

    bot = PipoBot(
        command_prefix=settings.commands.prefix, description=settings.bot_description
    )

    async with bot:
        await bot.add_cog(MusicBot(bot, channel, voice_channel))
        await bot.start(token)


if __name__ == "__main__":

    logging.basicConfig(
        encoding="utf-8",
        level=settings.log_level,
        format=settings.log_format,
    )

    asyncio.run(main())
