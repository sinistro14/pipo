#!usr/bin/env python3
import logging

from discord.ext import commands

from pipo.command import (
    Clear,
    CommandQueue,
    Leave,
    Pause,
    Play,
    Reboot,
    Resume,
    Skip,
)
from pipo.config import settings
from pipo.pipo import Pipo


class MusicBot(commands.Cog):
    """Music related collection of commands.

    Discord music bot to play audio.
    Functionality includes:
    - playing music from youtube video/playlist urls;
    - clear, skip, pause & resume audio.
    """

    _logger: logging.Logger

    def __init__(self, bot, channel_id, voice_channel_id):
        self._logger = logging.getLogger(__name__)
        self.bot = bot
        self.pipo = Pipo(self.bot)
        self.pipo.channel_id = channel_id
        self.pipo.voice_channel_id = voice_channel_id
        self.command_queue = CommandQueue()

    @commands.command(
        pass_context=True,
        brief="Remove bot from voice channel",
        help="Remove bot from voice channel.",
    )
    async def leave(self, ctx):  # noqa: D102
        self._logger.info("Received discord command leave")
        await self.command_queue.add(Leave(self.pipo, ctx))

    @commands.command(
        pass_context=True,
        brief="Play music",
        help="Add music by providing a youtube music/playlist url or search query.\n"
        "Use -q <query> to play the most related music.\n"
        "Use -s <url> to shuffle a playlist.\n"
        "-play [-q] [-s] <query> | <music_url> | <playlist_url>",
    )
    async def play(self, ctx, *query):  # noqa: D102
        self._logger.info("Received discord command play")
        option = query[0]
        shuffle = len(query) > 1 and option == settings.commands.shuffle
        search = len(query) > 1 and option == settings.commands.search
        if shuffle:
            query = query[1:]
        elif search:
            query = " ".join(query[1:])
        else:
            option = ""
        self._logger.info(
            "Received play query %s with option '%s'",
            query,
            option,
        )
        await self.command_queue.add(Play(self.pipo, ctx, query, shuffle))

    @commands.command(
        pass_context=True,
        brief="Clear queued music",
        help="Clear queued music and bot state.",
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

    @commands.command(pass_context=True, brief="Restart bot")
    async def reboot(self, ctx):  # noqa: D102
        self._logger.info("Received discord command reboot")
        await self.command_queue.add(Reboot(self.pipo, ctx))
