import asyncio
from typing import List

import discord
from discord.ext.commands import Context as Dctx

import pipo.states.idle_state
import pipo.states.playing_state
import pipo.states.state


class DisconnectedState(pipo.states.state.State):
    """Bot disconnected state.

    Bot state while not connected to a voice channel.
    Can process commands:
        * :meth:`join`
        * :meth:`play`
    """

    def __init__(self):
        super().__init__("disconnected")

    async def _join(self, ctx: Dctx) -> None:
        """Make bot connect to voice channel."""
        self._logger.debug("Join requested", extra=dict(data=ctx.author.name))
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            channel = self.context.bot.get_channel(self.context.voice_channel_id)
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
            self._logger.info(
                "Successfully joined channel", extra=dict(data=channel.name)
            )
        except (asyncio.TimeoutError, discord.ClientException):
            self._logger.exception("Error joining channel")
        finally:
            self.context.voice_client = ctx.voice_client
            await self.context.move_message(ctx)

    async def join(self, ctx: Dctx) -> None:
        """Make bot connect to voice channel.

        Connect bot to voice channel and change state to Idle.

        Parameters
        ----------
        ctx : Dctx
            Bot context.
        """
        await self._join(ctx)
        self.context.transition_to(pipo.states.idle_state.IdleState())

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        """Make bot connect to voice channel.

        Connect bot to voice channel and play a music, changing the state to Playing.
        query : List[str]
            Music to play.
        shuffle : bool, optional
            Randomize play order when multiple musics are provided.
        """
        await self._join(ctx)
        self.context.player.play(query, shuffle)
        self.context.transition_to(pipo.states.playing_state.PlayingState())

    async def skip(self) -> None: # noqa: D102
        pass

    async def leave(self) -> None: # noqa: D102
        pass

    async def resume(self) -> None: # noqa: D102
        pass

    async def stop(self) -> None: # noqa: D102
        pass

    async def pause(self) -> None: # noqa: D102
        pass
