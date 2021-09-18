import discord
import pafy
import urllib
import re
from discord.ext import commands


FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
TOKEN = 'ODg4NTM2NzY2ODU0ODY5MDMy.YUUIWQ.4mgXJv5ufyoP4xjHQaahytVfyl0'

client = commands.Bot(command_prefix = '-')
voiceClient = None
musicQueue = []


def getYoutubeAudio(query):
    if(not query.startswith("http")):
        query = query.replace(" ", "+")
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        query = video_ids[0]
        
    pafyObj = pafy.new(query)
    audioUrl = pafyObj.getbestaudio().url
    return audioUrl


def playNextMusic(error=None):
    if(len(musicQueue) == 0):
        return
    url = musicQueue.pop(0)
    voiceClient.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=playNextMusic)


@client.event
async def on_ready():
    print('Putos Groovy is ready!')


@client.command(pass_context=True)
async def join(ctx):
    musicQueue.clear()
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command(pass_context=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()
    

@client.command(pass_context=True)
async def play(ctx, *query):
    if(ctx.voice_client == None):
        await join(ctx)

    query = ' '.join(query)
    url = getYoutubeAudio(query)
    musicQueue.append(url)
    
    vc = ctx.voice_client
    if(not vc.is_playing()):
        global voiceClient
        voiceClient = vc
        playNextMusic()


@client.command(pass_context=True)
async def stop(ctx):
    vc = ctx.voice_client
    if(vc != None and vc.is_playing()):
        musicQueue.clear()
        vc.stop()


@client.command(pass_context=True)
async def pause(ctx):
    vc = ctx.voice_client
    if(vc != None and vc.is_playing()):
        vc.pause()


@client.command(pass_context=True)
async def resume(ctx):
    vc = ctx.voice_client
    if(vc != None and vc.is_paused()):
        vc.resume()


@client.command(pass_context=True)
async def skip(ctx):
    vc = ctx.voice_client
    if(len(musicQueue) == 0 or vc == None):
        return
    if(vc.is_playing()):
        vc.stop()


@client.event
async def on_message(message):
    await client.process_commands(message)

    if message.author.name == "Kromos":
        await message.add_reaction("<:FineKromos:872247061158953010>")
        return
    
##    if message.content.startswith('$hello'):
##        await message.channel.send('Hello!')
    


client.run(TOKEN)
