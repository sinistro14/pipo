from typing import List

from discord.ext.commands import Context as Dctx

from pipo.states.state import State
from pipo.states.idle_state import IdleState
from pipo.states.disconnected_state import DisconnectedState


class PlayingState(State):
    async def stop(self) -> None:
        self.context._player.stop()
        self.context.transition_to(IdleState())

    async def pause(self) -> None:
        self.context._player.pause()
        self.context.transition_to(IdleState())

    async def leave(self) -> None:
        await self.context._player.leave()
        self.context.transition_to(DisconnectedState())

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        self.context._player.play(query, shuffle)

    async def skip(self) -> None:
        """Skip currently playing music.

        Skips currently playing music by stopping the voice client and
        removing such queue element.
        """
        self.context._voice_client.stop()
