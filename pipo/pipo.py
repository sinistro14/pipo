#!usr/bin/env python3
import logging
from typing import List

import discord.ext.commands
from discord.ext.commands import Context as Dctx

import pipo
import pipo.player
import pipo.states.idle_state
import pipo.states.disconnected_state
from pipo.config import settings

logging.basicConfig(encoding="utf-8", level=settings.log_level)

class Pipo(pipo.states.Context):

    _logger: logging.Logger
    bot: discord.ext.commands.Bot
    voice_client: discord.VoiceClient
    music_channel: discord.VoiceChannel
    player: pipo.player.Player

    def __init__(self, bot: discord.ext.commands.Bot):
        super().__init__(pipo.states.disconnected_state.DisconnectedState())
        self._logger = logging.getLogger(__name__)
        self.channel_id = None
        self.voice_channel_id = None

        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.bot = bot
        self.voice_client = None
        self.music_channel = None
        self.player = pipo.player.Player(self)

    def current_state(self) -> str:
        return self._state.__name__  # noqa

    def become_idle(self) -> None:
        self.transition_to(pipo.states.idle_state.IdleState())

    def queue_size(self) -> int:
        return self.player.queue_size()

    async def send_message(self, message: str) -> None:
        if not self.music_channel:
            self.music_channel = self.bot.get_channel(self.channel_id)
        await self.music_channel.send(message)

    async def submit_music(self, url: str) -> None:  # noqa
        try:
            self._logger.info(
                f"can_play flag before voice client play: {self.player.can_play.is_set()}"
            )
            self.voice_client.play(
                discord.FFmpegPCMAudio(url, **self._ffmpeg_options),
                after=self.player.can_play.set(),
            )
            self._logger.info(
                f"can_play flag after voice client play: {self.player.can_play.is_set()}"
            )
        except discord.ClientException:
            self._logger.warn("Unable to play music in Discord voice channel.")

    async def join(self, ctx: Dctx):
        self._logger.info("Joined channel")
        await self._state.join(ctx)

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool):
        await self._state.play(ctx, query, shuffle)
        await self.move_message(ctx)

    async def pause(self, ctx: Dctx):
        await self._state.pause()
        await self.move_message(ctx)

    async def resume(self, ctx: Dctx):
        await self._state.resume()
        await self.move_message(ctx)

    async def stop(self, ctx: Dctx):
        await self._state.stop()
        await self.move_message(ctx)

    async def leave(self, ctx: Dctx):
        await self._state.leave()
        await self.move_message(ctx)

    async def skip(self, ctx: Dctx):
        await self._state.skip()
        await self.move_message(ctx)

    async def reboot(self, ctx: Dctx):
        await self._state.leave()  # transitions to Disconnected state
        await self.join(ctx)  # transitions to Idle state

    async def shuffle(self, ctx: Dctx):
        self.player.shuffle()
        await self.move_message(ctx)

    async def move_message(self, ctx: Dctx):
        msg = ctx.message
        content = msg.content.encode("ascii", "ignore").decode()
        await msg.delete(delay=settings.pipo.move_message_delay)
        await self.send_message(f"{msg.author.name} {content}")
