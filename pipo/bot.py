#!usr/bin/env python3
import logging

import discord
from discord.ext import commands

from pipo.pipo import Pipo
from pipo.config import settings
from pipo.command import (
    Join,
    Play,
    Skip,
    Stop,
    Leave,
    Pause,
    Reboot,
    Resume,
    Status,
    Shuffle,
    CommandQueue,
    ListCommands,
)

logger = logging.getLogger(__name__)


class MusicBot(commands.Cog):
    def __init__(self, bot, channel_id, voice_channel_id):
        self.bot = bot
        self.pipo = Pipo(self.bot)
        self.pipo.channel_id = channel_id
        self.pipo.voice_channel_id = voice_channel_id
        self.command_queue = CommandQueue()

    @commands.command(pass_context=True)
    async def join(self, ctx):
        logger.info("Received discord command join.")
        await self.command_queue.add(Join(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        logger.info("Received discord command leave.")
        await self.command_queue.add(Leave(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def play(self, ctx, *query):
        logger.info("Received discord command play.")
        shuffle = len(query) > 1 and query[0] == settings.command.commands.shuffle
        if shuffle:
            query = query[1:]
        logger.info(f"Received play query: {query}")
        await self.command_queue.add(Play(self.pipo, ctx, query, shuffle))

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        logger.info("Received discord command stop.")
        await self.command_queue.add(Stop(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        logger.info("Received discord command pause.")
        await self.command_queue.add(Pause(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        logger.info("Received discord command resume.")
        await self.command_queue.add(Resume(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        logger.info("Received discord command skip.")
        await self.command_queue.add(Skip(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def shuffle(self, ctx):
        logger.info("Received discord command shuffle.")
        await self.command_queue.add(Shuffle(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def listcommands(self, ctx):
        logger.info("Received discord command listcommands.")
        await self.command_queue.add(ListCommands(self.pipo))

    @commands.command(pass_context=True)
    async def status(self, ctx):
        logger.info("Received discord command status.")
        await self.command_queue.add(Status(self.pipo, ctx))

    @commands.command(pass_context=True)
    async def reboot(self, ctx):
        logger.info("Received discord command reboot.")
        await self.command_queue.add(Reboot(self.pipo, ctx))


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=settings.command.commands.prefix,
    case_insensitive=True,
    intents=intents,
)


@bot.event
async def on_ready():
    logger.info("Pipo do Arraial is ready.")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
