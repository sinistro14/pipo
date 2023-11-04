#!usr/bin/env python3
import asyncio
import logging

from pipo.signal_manager import SignalManager
from pipo.bot import PipoBot
from pipo.cogs import MusicBot
from pipo.config import settings


async def main():

    channel = settings.channel
    voice_channel = settings.voice_channel
    token = settings.token

    SignalManager.add_handlers(asyncio.get_event_loop())

    bot = PipoBot(
        command_prefix=settings.commands.prefix, description=settings.bot_description
    )

    try:
        async with bot:
            await bot.add_cog(MusicBot(bot, channel, voice_channel))
            await bot.start(token)
    except Exception:
        logging.getLogger(__name__).exception("Unexpected exception raised.")


if __name__ == "__main__":

    logging.basicConfig(
        encoding="utf-8",
        level=settings.log_level,
        format=settings.log_format,
    )

    asyncio.run(main())
