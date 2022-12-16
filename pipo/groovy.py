import random
import re
import urllib
import logging

import discord
from discord.ext.commands import Bot
from discord.ext.commands import Context as Dctx
from pytube import Playlist, YouTube

from pipo.music import MusicQueue
from pipo.states import Context, DisconnectedState, IdleState

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO) 

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

    _bot: Bot
    _voice_client: discord.VoiceClient
    _music_channel: discord.VoiceChannel
    _music_queue: MusicQueue

    def __init__(self, bot: Bot):
        self.channel_id = None
        self.voice_channel_id = None

        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self._bot = bot
        self._voice_client = None
        self._music_channel = None
        self._music_queue = MusicQueue()

        self.transition_to(DisconnectedState())

    async def onReady(self):
        self._music_channel = self._bot.get_channel(self.channel_id)
        logger.info("Pipo do Arraial is ready.")

    async def process(self, event, ctx: Dctx):
        if not ctx.author.voice:
            return
        newState = await self.currentState.process(event, ctx)
        if newState:
            self.transition_to(newState)

    async def send_message(self, message: str) -> None:
        await self._music_channel.send(message)

    async def join(self, ctx: Dctx):
        self._music_queue.clear()
        channel = ctx.author.voice.channel
        if not channel:
            channel = self._bot.get_channel(self.voice_channel_id) # default channel
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
            logger.debug("Joined successfully.")
        except:
            logger.exception("Error on joining a channel.")
        finally:
            self._voice_client = ctx.voice_client
            if "_query_" not in ctx.kwargs:
                await self._moveMessage(ctx)
            # self._startIdleCounter()

    async def joinAndPlay(self, ctx: Dctx):
        await self.join(ctx)
        await self.play(ctx)

    async def joinAndPlayList(self, ctx: Dctx):
        await self.join(ctx)
        await self.playList(ctx)

    def playNextMusic(self):
        nextQuery = self._music_queue.pop()
        logger.debug(f"Next music: {nextQuery} | Queue size: {len(self._music_queue)}")
        if not nextQuery:
            self.transition_to(IdleState())
        else:
            try:
                nextUrl = self._getYoutubeAudio(nextQuery)
                self._voice_client.play(
                    discord.FFmpegPCMAudio(nextUrl, **self._ffmpeg_options),
                    after=self.playNextMusic,
                )
            except Exception as e:
                logger.warning(f"Can not play next music. Error: {str(e)}")
                self._music_channel.send("Can not play next music. Skipping...")
                self.playNextMusic()

    async def play(self, ctx: Dctx):
        self._music_queue.add(ctx.kwargs["_query_"])
        if not self._voice_client.is_playing() and not self._voice_client.is_paused():
            self.playNextMusic()
        await self._moveMessage(ctx)

    async def playList(self, ctx: Dctx, shuffle: bool):
        plist = list(Playlist(ctx.kwargs["_query_"]))
        if len(plist):
            if shuffle:
                random.shuffle(plist)
            self._music_queue.add(plist)
            if not self._voice_client.is_playing() and not self._voice_client.is_paused():
                self.playNextMusic()
        await self._moveMessage(ctx)

    async def pause(self, ctx: Dctx):
        await self._voice_client.pause()
        await self._moveMessage(ctx)

    async def resume(self, ctx: Dctx):
        await self._voice_client.resume()
        await self._moveMessage(ctx)

    async def stop(self, ctx: Dctx):
        self._music_queue.clear()
        await self._moveMessage(ctx)
        await self._voice_client.stop()

    async def leave(self, ctx: Dctx):
        await self._voice_client.disconnect()
        await self._moveMessage(ctx)
        #self._stopIdleCounter()

    async def skip(self, ctx: Dctx):
        await self._moveMessage(ctx)
        await self._voice_client.stop()

    async def skipList(self, ctx: Dctx):
        await self._moveMessage(ctx)
        self._music_queue.pop()
        await self._voice_client.stop()

    async def reboot(self):
        self.transition_to(DisconnectedState())
        await self.join()

    async def shuffle(self, ctx: Dctx):
        self._music_queue.shuffle()

    def _getYoutubeAudio(self, query):
        if not query.startswith("http"):
            query = query.replace(" ", "+").encode("ascii", "ignore").decode()
            html = urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={query}"
            )
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            query = f"https://www.youtube.com/watch?v={video_ids[0]}"

        return YouTube(query).streams.get_audio_only().url

    async def _moveMessage(self, ctx: Dctx):
        msg = ctx.message
        content = msg.content.encode("ascii", "ignore").decode()
        await self._music_channel.send(f"{msg.author.name} {content}")
        await msg.delete()
