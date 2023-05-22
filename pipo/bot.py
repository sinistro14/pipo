#!usr/bin/env python3

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

bot = commands.Bot(command_prefix="-", case_insensitive=True, intents=intents)
pipo = Pipo(bot)

command_queue = CommandQueue(settings.command.queue.max_workers)


@bot.event
async def on_ready():
    await pipo.on_ready()


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command
async def join(ctx):
    command_queue.add(Join(pipo, ctx))


@bot.command
async def leave(ctx):
    command_queue.add(Leave(pipo, ctx))


@bot.command
async def play(ctx, *query):
    shuffle = len(query) > 1 and query[0] == settings.command.queue.max_workers
    if shuffle:
        query = query[1:]
    command_queue.add(Play(pipo, ctx, query, shuffle))


@bot.command
async def stop(ctx):
    command_queue.add(Stop(pipo, ctx))


@bot.command
async def pause(ctx):
    command_queue.add(Pause(pipo, ctx))


@bot.command
async def resume(ctx):
    command_queue.add(Resume(pipo, ctx))


@bot.command
async def skip(ctx):
    command_queue.add(Skip(pipo, ctx))


@bot.command
async def shuffle(ctx):
    command_queue.add(Shuffle(pipo, ctx))


@bot.command
async def listcommands(ctx):
    command_queue.add(ListCommands(pipo))


@bot.command
async def status(ctx):
    command_queue.add(Status(pipo, ctx))


@bot.command
async def reboot(ctx):
    command_queue.add(Reboot(pipo, ctx))
