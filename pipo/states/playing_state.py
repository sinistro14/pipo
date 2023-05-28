from typing import List

from discord.ext.commands import Context as Dctx

import pipo.states.state
import pipo.states.idle_state
import pipo.states.disconnected_state


class PlayingState(pipo.states.state.State):
    def __init__(self):
        super().__init__("playing")

    async def join(self, ctx: Dctx) -> None:
        pass

    async def resume(self) -> None:
        pass

    async def stop(self) -> None:
        self.context._player.stop()
        self.context.transition_to(pipo.states.idle_state.IdleState())

    async def pause(self) -> None:
        self.context._player.pause()
        self.context.transition_to(pipo.states.idle_state.IdleState())

    async def leave(self) -> None:
        await self.context._player.leave()
        self.context.transition_to(pipo.states.disconnected_state.DisconnectedState())

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        self.context._player.play(query, shuffle)

    async def skip(self) -> None:
        """Skip currently playing music.

        Skips currently playing music by stopping the voice client, currently playing
        the music.
        """
        self.context._voice_client.stop()
