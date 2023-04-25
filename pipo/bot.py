#!usr/bin/env python3

import discord
from discord.ext import commands

from pipo.config import settings
from pipo.groovy import Groovy
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
    PlayList,
    SkipList,
    CommandQueue,
    ListCommands,
)

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="-", case_insensitive=True, intents=intents)
groovy = Groovy(bot)

command_queue = CommandQueue(settings.command.queue.max_workers)


@bot.event
async def on_ready():
    await groovy.on_ready()


@bot.command(pass_context=True)
async def join(ctx):
    command_queue.add(Join(groovy, ctx))


@bot.command(pass_context=True)
async def leave(ctx):
    command_queue.add(Leave(groovy, ctx))


@bot.command(pass_context=True)
async def play(ctx, *query):
    command_queue.add(Play(groovy, ctx, query))


@bot.command(pass_context=True)
async def playlist(ctx, *query):
    command_queue.add(PlayList(groovy, ctx, query, False))


@bot.command(pass_context=True)
async def playlistshuffle(ctx, *query):
    command_queue.add(PlayList(groovy, ctx, query, True))


@bot.command(pass_context=True)
async def stop(ctx):
    command_queue.add(Stop(groovy, ctx))


@bot.command(pass_context=True)
async def pause(ctx):
    command_queue.add(Pause(groovy, ctx))


@bot.command(pass_context=True)
async def resume(ctx):
    command_queue.add(Resume(groovy, ctx))


@bot.command(pass_context=True)
async def skip(ctx):
    command_queue.add(Skip(groovy, ctx))


@bot.command(pass_context=True)
async def skiplist(ctx):
    command_queue.add(SkipList(groovy, ctx))


@bot.command(pass_context=True)
async def shuffle(ctx):
    command_queue.add(Shuffle(groovy, ctx))


@bot.command(pass_context=True)
async def listcommands(ctx):
    command_queue.add(ListCommands(groovy))


@bot.command(pass_context=True)
async def status(ctx):
    command_queue.add(Status(groovy, ctx))


@bot.command(pass_context=True)
async def reboot(ctx):
    command_queue.add(Reboot(groovy, ctx))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
