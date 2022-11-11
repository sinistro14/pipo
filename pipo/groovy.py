import random
import re
import urllib

import discord
import pafy
import psutil
from pytube import Playlist

from pipo.music import MusicQueue
from pipo.states import Context, DisconnectedState, IdleState, State

"""
class State:
    def __init__(self, name):
        self.name = name
        self.transitions = []

    def addTransition(self, event, action, nextState):
        transition = Transition(event, action, nextState)
        self.transitions.append(transition)

    async def process(self, event, msg):
        for transition in self.transitions:
            if event == transition.event:
                try:
                    await transition.action(msg)
                except:
                    pass
                finally:
                    return transition.nextState
        return None
"""


class Groovy(Context):
    def __init__(self, bot):
        self.channel_id = None

        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.bot = bot
        self.voiceClient = None
        self.musicChannel = None
        self.musicQueue = MusicQueue()

        self.transition_to(DisconnectedState())

    async def onReady(self):
        self.musicChannel = self.bot.get_channel(self.channel_id)

    async def process(self, event, ctx):
        if not ctx.author.voice:
            return
        newState = await self.currentState.process(event, ctx)
        if newState:
            self.transition_to(newState)

    async def join(self, ctx):
        self.musicQueue.clear()
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
        except:
            pass
        finally:
            self.voiceClient = ctx.voice_client
            if "_query_" not in ctx.kwargs:
                await self._moveMessage(ctx)
            # self._startIdleCounter()

    async def joinAndPlay(self, ctx):
        await self.join(ctx)
        await self.play(ctx)

    async def joinAndPlayList(self, ctx):
        await self.join(ctx)
        await self.playList(ctx)

    def playNextMusic(self):
        nextQuery = self.musicQueue.pop()
        if not nextQuery:
            self.transition_to(IdleState())
        else:
            try:
                nextUrl = self._getYoutubeAudio(nextQuery)
                self.voiceClient.play(
                    discord.FFmpegPCMAudio(nextUrl, **self._ffmpeg_options),
                    after=self.playNextMusic,
                )
            except:
                self.musicChannel.send("Can not play next music. Skipping...")
                self.playNextMusic()

    async def play(self, ctx):
        self.musicQueue.add(ctx.kwargs["_query_"])
        if not self.voiceClient.is_playing() and not self.voiceClient.is_paused():
            self.playNextMusic()
        await self._moveMessage(ctx)

    async def playList(self, ctx):
        plist = list(Playlist(ctx.kwargs["_query_"]))
        if len(plist):
            if "_shuffle_" in ctx.kwargs and ctx.kwargs["_shuffle_"]:
                random.shuffle(plist)
            self.musicQueue.add(plist)
            if not self.voiceClient.is_playing() and not self.voiceClient.is_paused():
                self.playNextMusic()
        await self._moveMessage(ctx)

    async def pause(self, ctx):
        await self.voiceClient.pause()
        await self._moveMessage(ctx)

    async def resume(self, ctx):
        await self.voiceClient.resume()
        await self._moveMessage(ctx)

    async def stop(self, ctx):
        self.musicQueue.clear()
        await self._moveMessage(ctx)
        await self.voiceClient.stop()

    async def leave(self, ctx):
        await self.voiceClient.disconnect()
        await self._moveMessage(ctx)
        self._stopIdleCounter()

    async def skip(self, ctx):
        await self._moveMessage(ctx)
        await self.voiceClient.stop()

    async def skipList(self, ctx):
        await self._moveMessage(ctx)
        self.musicQueue.pop()
        await self.voiceClient.stop()

    async def reboot(self):
        self.transition_to(DisconnectedState())
        await self.join()

    async def shuffle(self, ctx):
        self.musicQueue.shuffle()
        await self._moveMessage(ctx)

    def _getYoutubeAudio(self, query):
        if not query.startswith("http"):
            query = query.replace(" ", "+").encode("ascii", "ignore").decode()
            html = urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={query}"
            )
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            query = video_ids[0]

        pafyObj = pafy.new(query)
        audioUrl = pafyObj.getbestaudio().url
        return audioUrl

    async def _moveMessage(self, ctx):
        msg = ctx.message
        content = msg.content.encode("ascii", "ignore").decode()
        await self.musicChannel.send(msg.author.name + "  " + content)
        await msg.delete()

    async def showCommandList(self):
        await self.musicChannel.send(
            "Command List: \n "
            " -join \n"
            " -play <query / url> \n"
            " -pause \n"
            " -resume \n"
            " -skip \n"
            " -stop \n"
            " -leave \n"
            " -playlist <url> \n"
            " -playlistshuffle <url> \n"
            " -skiplist \n"
            " -state \n"
            " -help"
        )

    async def showStatus(self, ctx):
        await self._moveMessage(ctx)
        await self.musicChannel.send(
            f"Current State: {self.currentState.name}\n"
            f"Queue Length: {self.musicQueue.getLength()}\n"
            f"CPU Usage: {psutil.cpu_percent()} \n"
            f"RAM Usage: {psutil.virtual_memory().percent}%\n"
            f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
            f"Temperature: {psutil.sensors_temperatures()['cpu_thermal'][0][1]} ºC"
        )
