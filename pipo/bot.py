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

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=settings.command.commands.prefix,
    case_insensitive=True,
    intents=intents,
)
pipo = Pipo(bot)

command_queue = CommandQueue()

logger = logging.getLogger(__name__)


@bot.event
async def on_ready():
    await pipo.on_ready()


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command
async def join(ctx):
    logger.info("Received discord command join.")
    await command_queue.add(Join(pipo, ctx))


@bot.command
async def leave(ctx):
    logger.info("Received discord command leave.")
    await command_queue.add(Leave(pipo, ctx))


@bot.command
async def play(ctx, *query):
    logger.info("Received discord command play.")
    shuffle = len(query) > 1 and query[0] == settings.command.commands.shuffle
    if shuffle:
        query = query[1:]
    await command_queue.add(Play(pipo, ctx, query, shuffle))


@bot.command
async def stop(ctx):
    logger.info("Received discord command stop.")
    await command_queue.add(Stop(pipo, ctx))


@bot.command
async def pause(ctx):
    logger.info("Received discord command pause.")
    await command_queue.add(Pause(pipo, ctx))


@bot.command
async def resume(ctx):
    logger.info("Received discord command resume.")
    await command_queue.add(Resume(pipo, ctx))


@bot.command
async def skip(ctx):
    logger.info("Received discord command skip.")
    await command_queue.add(Skip(pipo, ctx))


@bot.command
async def shuffle(ctx):
    logger.info("Received discord command shuffle.")
    await command_queue.add(Shuffle(pipo, ctx))


@bot.command
async def listcommands(ctx):
    logger.info("Received discord command listcommands.")
    await command_queue.add(ListCommands(pipo))


@bot.command
async def status(ctx):
    logger.info("Received discord command status.")
    await command_queue.add(Status(pipo, ctx))


@bot.command
async def reboot(ctx):
    logger.info("Received discord command reboot.")
    await command_queue.add(Reboot(pipo, ctx))
