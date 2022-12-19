from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.states.disconnected_state import DisconnectedState
from pipo.states.idle_state import IdleState
from pipo.states.state import State


class PlayingState(State):
    context: Groovy

    async def stop(self, ctx: Dctx) -> None:
        self.context._music_queue.clear()
        await self.context._move_message(ctx)
        await self.context._voice_client.stop()
        self.context.transition_to(IdleState())

    async def pause(self, ctx: Dctx) -> None:
        await self.context._voice_client.pause()
        await self.context._move_message(ctx)
        self.context.transition_to(IdleState())

    async def leave(self, ctx: Dctx) -> None:
        await self.context._voice_client.disconnect()
        await self.context._move_message(ctx)
        self.context.transition_to(DisconnectedState())

    async def play(self, ctx: Dctx) -> None:
        await self.context._play(ctx)

    async def play_list(self, ctx: Dctx) -> None:
        await self.context._play_list(ctx)

    async def skip(self, ctx: Dctx, skip_list: bool) -> None:
        await self.context._move_message(ctx)
        if skip_list:
            self.context._music_queue.skip_list()
        await self.context._voice_client.stop()

    def skip_list(self) -> None:
        self.context.skip()
