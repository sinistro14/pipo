import asyncio
from typing import List

import discord
from discord.ext.commands import Context as Dctx

import pipo.states.state
import pipo.states.idle_state
import pipo.states.playing_state


class DisconnectedState(pipo.states.state.State):
    def __init__(self):
        super().__init__("disconnected")

    async def _join(self, ctx: Dctx) -> None:
        channel = ctx.author.voice.channel or self.context._bot.get_channel(
            self.context.voice_channel_id
        )
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
            self._logger.debug("Successfully joined channel %s.", channel.name)
        except (asyncio.TimeoutError, discord.ClientException):
            self._logger.exception("Error while joining channel.")
        finally:
            self._voice_client = ctx.voice_client
            await self.context.move_message(ctx)

    async def join(self, ctx: Dctx) -> None:
        await self._join(ctx)
        self.context.transition_to(pipo.states.idle_state.IdleState())

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        await self._join(ctx)
        self.context._player.play(query, shuffle)
        self.context.transition_to(pipo.states.playing_state.PlayingState())

    def skip(self) -> None:
        pass

    async def leave(self) -> None:
        pass

    async def resume(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def pause(self) -> None:
        pass
