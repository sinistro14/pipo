import asyncio
import random as rd
import re
import urllib
import logging


import discord
import pafy
import psutil
from pytube import Playlist


logger = logging.getLogger("groovy")

class BotEvent:
    JOIN = 1
    LEAVE = 2
    PLAY = 3
    STOP = 4
    PAUSE = 5
    RESUME = 6
    SKIP = 7
    PLAYLIST = 8
    SKIPLIST = 9
    HELP = 10


class Transition:
    def __init__(self, event, action, nextState):
        self.event = event
        self.action = action
        self.nextState = nextState


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


class Queue:
    def __init__(self):
        self.queue = []

    def add(self, url):
        self.queue.append(url)

    def remove(self, index):
        if len(self.queue) > index:
            del self.queue[index]

    def clear(self):
        self.queue.clear()

    def pop(self):
        if not len(self.queue):
            return None
        elif isinstance(self.queue[0], str):
            return self.queue.pop(0)
        else:
            val = self.queue[0].pop(0)
            if not len(self.queue[0]):
                del self.queue[0]
            return val

    def shuffle(self):
        for item in self.queue:
            if isinstance(item, list):
                rd.shuffle(item)

        if len(self.queue):
            rd.shuffle(self.queue)

    def isGroup(self):
        return isinstance(self.queue[0], list)

    def getLength(self):
        count = 0
        for item in self.queue:
            count += len(item) if isinstance(item, list) else 1
        return count


class Groovy:
    def __init__(self, bot):
        self.channel_id = None
        self.voiceChannel_id = None
        self._idle_duration = 60 * 30  ## 30m
        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        
        self.bot = bot
        self.voiceClient = None
        self.musicChannel = None
        self.musicQueue = Queue()
        self.idleCounter = None

        self.disconnectedState = State("Disconnected")
        self.idleState = State("Idle")
        self.playingState = State("Playing")

        self.currentState = self.disconnectedState

        self.disconnectedState.addTransition(BotEvent.JOIN, self.join, self.idleState)
        self.disconnectedState.addTransition(
            BotEvent.PLAY, self.joinAndPlay, self.playingState
        )
        self.disconnectedState.addTransition(
            BotEvent.PLAYLIST, self.joinAndPlayList, self.playingState
        )
        self.idleState.addTransition(BotEvent.PLAY, self.play, self.playingState)
        self.idleState.addTransition(
            BotEvent.PLAYLIST, self.playList, self.playingState
        )
        self.idleState.addTransition(BotEvent.LEAVE, self.leave, self.disconnectedState)
        self.idleState.addTransition(BotEvent.RESUME, self.resume, self.playingState)
        self.playingState.addTransition(BotEvent.STOP, self.stop, self.idleState)
        self.playingState.addTransition(BotEvent.PAUSE, self.pause, self.idleState)
        self.playingState.addTransition(
            BotEvent.LEAVE, self.leave, self.disconnectedState
        )
        self.playingState.addTransition(BotEvent.PLAY, self.play, None)
        self.playingState.addTransition(BotEvent.PLAYLIST, self.playList, None)
        self.playingState.addTransition(BotEvent.SKIP, self.skip, None)
        self.playingState.addTransition(BotEvent.SKIPLIST, self.skipList, None)

    def setCurrentState(self, state):
        self.currentState = state
        logger.info("Set Current State = " + self.currenState.name)


    async def onReady(self):
        logger.info('Pipo do Arraial is ready!')
        self.musicChannel = self.bot.get_channel(self.channel_id)

    async def process(self, event, ctx):
        newState = await self.currentState.process(event, ctx)
        if newState:
            self.currenState = self.setCurrentState(newState)
        logger.info("Current State = " + self.currenState.name)

    async def join(self, ctx):
        self.musicQueue.clear()
        channel = ctx.author.voice.channel
        if(channel == None):
            channel = self.bot.get_channel(self.voiceChannel_id) # default channel
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
            logger.debug("Joined successfully")
        except Exception as e:
            logger.warning("Error on joining a channel | " + str(e))
            pass
        finally:
            self.voiceClient = ctx.voice_client
            if "_query_" not in ctx.kwargs:
                await self._moveMessage(ctx)
            self._startIdleCounter()

    async def joinAndPlay(self, ctx):
        await self.join(ctx)
        await self.play(ctx)

    async def joinAndPlayList(self, ctx):
        await self.join(ctx)
        await self.playList(ctx)

    def playNextMusic(self, error=None):
        nextQuery = self.musicQueue.pop()
        logger.debug("Next music = {} | In queue = {}".format(nextQuery, self.musicQueue.getLength()))
        if not nextQuery:
            self.setCurrentState(self.idleState)
        else:
            try:
                nextUrl = self._getYoutubeAudio(nextQuery)
                self.voiceClient.play(
                    discord.FFmpegPCMAudio(nextUrl, **self._ffmpeg_options),
                    after=self.playNextMusic,
                )
            except Exception as e:
                logger.warning("Can not play next music | " + str(e))
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
                rd.shuffle(plist)
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
        if self.musicQueue.isGroup():
            self.musicQueue.remove(0)
            await self.voiceClient.stop()

    async def reboot(self):
        self.setCurrentState(self.disconnectedState)
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

    def _startIdleCounter(self):
        if self.idleCounter:
            self.idleCounter.cancel()
        self.idleCounter = asyncio.ensure_future(self._idleTimeTask())

    def _stopIdleCounter(self):
        if self.idleCounter:
            self.idleCounter.cancel()
            self.idleCounter = None

    async def _idleTimeTask(self):
        idleTime = 0
        dT = 60 * 5
        while True:
            await asyncio.sleep(dT)

            if self.currentState.name != self.playingState.name:
                idleTime = idleTime + dT
            else:
                idleTime = 0

            if idleTime >= self._idle_duration:
                self.setCurrentState(self.disconnectedState)
                await self.musicChannel.send("Bye Bye !!!")
                await self.voiceClient.disconnect()
                break

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


##    def addToQueue(self, ctx):
##        query = ctx.kwargs["_query_"]
##        url = self._getYoutubeAudio(query)
##        self.musicQueue.add(url)
##
##
##    def addListToQueue(self, playlist):
##        audioUrls = []
##        for music in playlist:
##            audioUrls.append(self._getYoutubeAudio(music))
##        self.musicQueue.add(audioUrls)
