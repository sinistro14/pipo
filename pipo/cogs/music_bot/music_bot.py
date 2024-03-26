#!usr/bin/env python3
import logging

from discord.ext import commands

from pipo.cogs.music_bot.input_parser import InputParser
from pipo.command import (
    Clear,
    CommandQueue,
    Pause,
    Play,
    Reboot,
    Resume,
    Skip,
    Status,
)
from pipo.pipo import Pipo


class MusicBot(commands.Cog):
    """Music related collection of commands.

    Discord music bot to play audio.
    Functionality includes:
    - playing music from youtube video/playlist urls;
    - clear, skip, pause & resume audio.
    """

    _logger: logging.Logger
    __input_parser: InputParser

    def __init__(self, bot, channel_id, voice_channel_id):
        self._logger = logging.getLogger(__name__)
        self.bot = bot
        self.__input_parser = InputParser()
        self.pipo = Pipo(self.bot)
        self.pipo.channel_id = channel_id
        self.pipo.voice_channel_id = voice_channel_id
        self.command_queue = CommandQueue()

    @commands.command(
        pass_context=True,
        brief="Play music",
        help="Add music by providing a youtube music/playlist url or search query.\n"
        "Use -q <query> to search for the most related and popular music.\n"
        "Use -s <url> to shuffle a playlist.\n"
        "-play [-q] [-s] <query> | <music_url> | <playlist_url>",
    )
    async def play(self, ctx, *query):  # noqa: D102
        self._logger.info("Received discord command play: %s", query)
        args = self.__input_parser.parse_play(query)
        self._logger.info("Processed play command '%s'", args)
        if args and args.query:
            query = args.query
            query = " ".join(query) if args.search else query
            await self.command_queue.add(Play(self.pipo, ctx, query, args.shuffle))

    @commands.command(
        pass_context=True,
        brief="Clear bot state",
        help="Clear queued music, bot state and leave voice channel.",
    )
    async def clear(self, ctx):  # noqa: D102
        self._logger.info("Received discord command clear")
        await self.command_queue.add(Clear(self.pipo, ctx))

    @commands.command(
        pass_context=True,
        brief="Pause music",
        help="Pause currently playing music.",
    )
    async def pause(self, ctx):  # noqa: D102
        self._logger.info("Received discord command pause")
        await self.command_queue.add(Pause(self.pipo, ctx))

    @commands.command(
        pass_context=True,
        brief="Resume music",
        help="Resume playing previously paused music.",
    )
    async def resume(self, ctx):  # noqa: D102
        self._logger.info("Received discord command resume")
        await self.command_queue.add(Resume(self.pipo, ctx))

    @commands.command(
        pass_context=True,
        brief="Skip music",
        help="Skip currently playing music.",
    )
    async def skip(self, ctx):  # noqa: D102
        self._logger.info("Received discord command skip")
        await self.command_queue.add(Skip(self.pipo, ctx))

    @commands.command(
        pass_context=True,
        brief="Bot status",
        help="Bot queue status.",
    )
    async def status(self, ctx):  # noqa: D102
        self._logger.info("Received discord command status")
        await self.command_queue.add(Status(self.pipo, ctx))

    @commands.command(pass_context=True, brief="Restart bot")
    async def reboot(self, ctx):  # noqa: D102
        self._logger.info("Received discord command reboot")
        await self.command_queue.add(Reboot(self.pipo, ctx))
