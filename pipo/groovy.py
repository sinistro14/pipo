import logging
import random
import re
import urllib

import discord
from discord.ext.commands import Bot
from discord.ext.commands import Context as Dctx
from pytube import Playlist, YouTube

from pipo.music import Music, MusicQueue
from pipo.states import Context, DisconnectedState, IdleState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Groovy(Context):

    _bot: Bot
    _voice_client: discord.VoiceClient
    _music_channel: discord.VoiceChannel
    _music_queue: MusicQueue

    def __init__(self, bot: Bot):
        super().__init__()
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

    def current_state(self) -> str:
        return self._state.__name__

    def queue_size(self) -> int:
        return self._music_queue.count()

    async def on_ready(self):
        self._music_channel = self._bot.get_channel(self.channel_id)
        logger.info("Pipo do Arraial is ready.")

    async def process(self, event, ctx: Dctx):
        if not ctx.author.voice:
            return
        new_state = await self.currentState.process(event, ctx)
        if new_state:
            self.transition_to(new_state)

    async def send_message(self, message: str) -> None:
        await self._music_channel.send(message)

    async def join(self, ctx: Dctx):
        self._state.join(ctx)

    def _play_next_music(self):
        next_query = self._music_queue.pop()
        logger.debug(
            "Next music: %s | Queue size: %d", next_query, self._music_queue.count()
        )
        if not next_query:  # if queue is empty
            self.transition_to(IdleState())
        else:
            try:
                next_url = self._get_youtube_audio(next_query)
                self._voice_client.play(
                    discord.FFmpegPCMAudio(next_url, **self._ffmpeg_options),
                    after=self._play_next_music,
                )
            except Exception as exc:
                logger.warning("Can not play next music. Error: %s", str(exc))
                self._music_channel.send("Can not play next music. Skipping...")
                self._play_next_music()

    async def play(self, ctx: Dctx):
        await self._state.play(ctx)

    async def _play(self, ctx: Dctx):
        self._music_queue.add(Music(ctx.kwargs["_query_"]))
        if not self._voice_client.is_playing() and not self._voice_client.is_paused():
            self._play_next_music()
        await self._move_message(ctx)

    async def play_list(self, ctx: Dctx):
        await self._state.play_list(ctx)

    async def _play_list(self, ctx: Dctx, shuffle: bool):
        plist = list(Playlist(ctx.kwargs["_query_"]))
        if plist:
            if shuffle:
                random.shuffle(plist)
            self._music_queue.add(MusicQueue([Music(music) for music in plist]))
            if (
                not self._voice_client.is_playing()
                and not self._voice_client.is_paused()
            ):
                self._play_next_music()
        await self._move_message(ctx)

    async def pause(self, ctx: Dctx):
        await self._state.pause(ctx)

    async def resume(self, ctx: Dctx):
        await self._state.resume(ctx)

    async def stop(self, ctx: Dctx):
        await self._state.stop(ctx)

    async def leave(self, ctx: Dctx):
        await self._state.leave(ctx)

    async def skip(self, ctx: Dctx, skip_list: bool):
        await self._state.skip(ctx, skip_list)

    async def reboot(self, ctx: Dctx):
        self._state.leave()  # transitions to Disconnected state
        await self.join(ctx)  # transitions to Idle state

    def shuffle(self):
        self._music_queue.shuffle()

    @staticmethod
    def _get_youtube_audio(query):
        if not query.startswith("http"):
            query = query.replace(" ", "+").encode("ascii", "ignore").decode()
            with urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={query}"
            ) as response:
                video_ids = re.findall(r"watch\?v=(\S{11})", response.read().decode())
                query = f"https://www.youtube.com/watch?v={video_ids[0]}"
        return YouTube(query).streams.get_audio_only().url

    async def _move_message(self, ctx: Dctx):
        msg = ctx.message
        content = msg.content.encode("ascii", "ignore").decode()
        await self._music_channel.send(f"{msg.author.name} {content}")
        await msg.delete()
