from discord.ext.commands import Context as Dctx
from pytube import Playlist

from pipo.groovy import Groovy
from pipo.states.disconnected_state import DisconnectedState
from pipo.states.idle_state import IdleState
from pipo.states.state import State


class PlayingState(State):
    context: Groovy

    async def stop(self) -> None:
        self.context._player.stop()
        self.context.transition_to(IdleState())

    async def pause(self) -> None:
        self.context._player.pause()
        self.context.transition_to(IdleState())

    async def leave(self) -> None:
        await self.context._player.leave()
        self.context.transition_to(DisconnectedState())

    async def play(self, ctx: Dctx) -> None:
        self.context._player.play(ctx.kwargs["_query_"])

    async def play_list(self, ctx: Dctx, shuffle: bool) -> None:
        self.context._player.play(list(Playlist(ctx.kwargs["_query_"])), shuffle)

    async def skip(self, skip_list: bool) -> None:
        """Skip currently playing music.

        _extended_summary_

        Parameters
        ----------
        ctx : Dctx
            _description_
        skip_list : bool
            _description_
        """
        if skip_list:
            self.context._player.skip_list()
        self.context._voice_client.stop()
