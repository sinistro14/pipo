import discord
import asyncio
import random as rd
from discord.ext import commands
from groovy import *
import urllib.request
import time


while(True): # wait for internet connection
    try:
        urllib.request.urlopen("https://www.google.pt/")
        break
    except:
        time.sleep(5)

bot = commands.Bot(command_prefix = '-', case_insensitive=True)
groovy = Groovy(bot)



@bot.event
async def on_ready():
    print('Putos Groovy is ready!')
    await groovy.onReady()


@bot.command(pass_context=True)
async def join(ctx):
    await groovy.process(BotEvent.JOIN, ctx)


@bot.command(pass_context=True)
async def leave(ctx):
    await groovy.process(BotEvent.LEAVE, ctx)
    

@bot.command(pass_context=True)
async def play(ctx, *query):
    ctx.kwargs["_query_"] = ' '.join(query)
    await groovy.process(BotEvent.PLAY, ctx)


@bot.command(pass_context=True)
async def playlist(ctx, *query):
    ctx.kwargs["_query_"] = ' '.join(query)
    await groovy.process(BotEvent.PLAYLIST, ctx)


@bot.command(pass_context=True)
async def playlistshuffle(ctx, *query):
    ctx.kwargs["_query_"] = ' '.join(query)
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
    #await groovy.reboot()
    

@bot.event
async def on_message(message):
    await bot.process_commands(message)

##    if(message.author.name == "Kromos" and rd.random() < 0.1):
##        await message.add_reaction("<:FineKromos:872247061158953010>")
##        await message.channel.send('Hello!')
    


bot.run(TOKEN)

