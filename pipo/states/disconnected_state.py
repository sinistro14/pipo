import logging

from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.states.idle_state import IdleState
from pipo.states.playing_state import PlayingState
from pipo.states.state import State

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DisconnectedState(State):
    context: Groovy

    async def _join(self, ctx: Dctx) -> None:
        self.context._music_queue.clear()
        channel = ctx.author.voice.channel or self.context._bot.get_channel(
            self.context.voice_channel_id
        )
        try:
            await channel.connect()
            await ctx.guild.change_voice_state(
                channel=channel, self_mute=True, self_deaf=True
            )
            logger.debug("Successfully joined channel %s.", channel.name)
        except:
            logger.exception("Error while joining channel.")
        finally:
            self._voice_client = ctx.voice_client
            if "_query_" not in ctx.kwargs:
                await self.context._move_message(ctx)

    async def join(self, ctx: Dctx) -> None:
        await self._join(ctx)
        self.context.transition_to(IdleState())

    async def play(self, ctx: Dctx) -> None:
        await self._join(ctx)
        await self.context._play()
        self.context.transition_to(PlayingState())

    async def play_list(self, ctx: Dctx) -> None:
        await self._join(ctx)
        await self.context._play_list()
        self.context.transition_to(PlayingState())
