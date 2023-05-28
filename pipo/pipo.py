#!usr/bin/env python3
import logging
from typing import List

import discord.ext.commands
from discord.ext.commands import Context as Dctx

import pipo.player
import pipo.states.idle_state
import pipo.states.disconnected_state
from pipo.states import Context

logging.basicConfig(level=logging.INFO)


class Pipo(Context):

    _logger: logging.Logger
    _bot: discord.ext.commands.Bot
    _voice_client: discord.VoiceClient
    _music_channel: discord.VoiceChannel
    _player: pipo.player.Player

    def __init__(self, bot: discord.ext.commands.Bot):
        super().__init__(pipo.states.disconnected_state.DisconnectedState())
        self._logger = logging.getLogger(__name__)
        self.channel_id = None
        self.voice_channel_id = None

        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self._bot = bot
        self._voice_client = None
        self._music_channel = None
        self._player = pipo.player.Player(self)

    def current_state(self) -> str:
        return self._state.__name__

    def become_idle(self) -> None:
        self.transition_to(pipo.states.idle_state.IdleState())

    def queue_size(self) -> int:
        return self._player.queue_size()

    async def on_ready(self) -> None:
        self._music_channel = self._bot.get_channel(self.channel_id)
        self._logger.info("Pipo do Arraial is ready.")

    async def send_message(self, message: str) -> None:
        await self._music_channel.send(message)

    async def submit_music(self, url: str) -> None:
        self._voice_client.play(
            discord.FFmpegPCMAudio(url, **self._ffmpeg_options),
            after=self._player.can_play.set,
        )

    async def join(self, ctx: Dctx):
        self._state.join(ctx)

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
        self._state.leave()  # transitions to Disconnected state
        await self.join(ctx)  # transitions to Idle state

    async def shuffle(self, ctx: Dctx):
        self._player.shuffle()
        await self.move_message(ctx)

    async def move_message(self, ctx: Dctx):
        msg = ctx.message
        content = msg.content.encode("ascii", "ignore").decode()
        await self.send_message(f"{msg.author.name} {content}")
        await msg.delete()
