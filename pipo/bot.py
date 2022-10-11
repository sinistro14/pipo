#!usr/bin/env python3

import sys

from discord.ext import commands

from .groovy import BotEvent, Groovy

bot = commands.Bot(command_prefix="-", case_insensitive=True)
groovy = Groovy(bot)


@bot.event
async def on_ready():
    print("Putos Groovy is ready!")
    await groovy.onReady()


@bot.command(pass_context=True)
async def join(ctx):
    await groovy.process(BotEvent.JOIN, ctx)


@bot.command(pass_context=True)
async def leave(ctx):
    await groovy.process(BotEvent.LEAVE, ctx)


@bot.command(pass_context=True)
async def play(ctx, *query):
    ctx.kwargs["_query_"] = " ".join(query)
    await groovy.process(BotEvent.PLAY, ctx)


@bot.command(pass_context=True)
async def playlist(ctx, *query):
    ctx.kwargs["_query_"] = " ".join(query)
    await groovy.process(BotEvent.PLAYLIST, ctx)


@bot.command(pass_context=True)
async def playlistshuffle(ctx, *query):
    ctx.kwargs["_query_"] = " ".join(query)
    ctx.kwargs["_shuffle_"] = True
    await groovy.process(BotEvent.PLAYLIST, ctx)


@bot.command(pass_context=True)
async def stop(ctx):
    await groovy.process(BotEvent.STOP, ctx)


@bot.command(pass_context=True)
async def pause(ctx):
    await groovy.process(BotEvent.PAUSE, ctx)


@bot.command(pass_context=True)
async def resume(ctx):
    await groovy.process(BotEvent.RESUME, ctx)


@bot.command(pass_context=True)
async def skip(ctx):
    await groovy.process(BotEvent.SKIP, ctx)


@bot.command(pass_context=True)
async def skiplist(ctx):
    await groovy.process(BotEvent.SKIPLIST, ctx)


@bot.command(pass_context=True)
async def shuffle(ctx):
    await groovy.shuffle(ctx)


@bot.command(pass_context=True)
async def status(ctx):
    await groovy.showStatus(ctx)


@bot.command(pass_context=True)
async def reboot(ctx):
    sys.exit()
    # await groovy.reboot()


@bot.event
async def on_message(message):
    await bot.process_commands(message)
