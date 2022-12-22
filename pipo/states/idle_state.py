import asyncio

from discord.ext.commands import Context as Dctx
from pytube import Playlist

from pipo.groovy import Groovy
from pipo.states.disconnected_state import DisconnectedState
from pipo.states.playing_state import PlayingState
from pipo.states.state import State


class IdleState(State):

    context: Groovy
    _idle_tracker: asyncio.Future
    _idle_timeout: int

    def __init__(self, idle_timeout: int = 60 * 30) -> None:  # 30 minutes
        super().__init__()
        self._idle_timeout = idle_timeout
        self._start_idle_tracker()

    def _start_idle_tracker(self):
        self._idle_tracker = asyncio.ensure_future(self._idle_tracker_task())

    def _stop_idle_tracker(self):
        if self._idle_tracker:
            self._idle_tracker.cancel()
            self._idle_tracker = None

    async def _idle_tracker_task(self):
        await asyncio.sleep(self._idle_timeout)
        self.context.transition_to(DisconnectedState())
        await self.context._music_channel.send("Bye Bye !!!")
        await self.context._voice_client.disconnect()

    def _clean_transition_to(self, state: State) -> None:
        self._stop_idle_tracker()
        self.context.transition_to(state)

    async def play(self, ctx: Dctx) -> None:
        self.context._player.play(ctx.kwargs["_query_"])
        self._clean_transition_to(PlayingState())

    async def play_list(self, ctx: Dctx, shuffle: bool) -> None:
        self.context._player.play(list(Playlist(ctx.kwargs["_query_"])), shuffle)
        self._clean_transition_to(PlayingState())

    async def leave(self) -> None:
        await self.context._voice_client.disconnect()
        self.context.transition_to(DisconnectedState())

    async def resume(self) -> None:
        self.context._player.resume()
        self._clean_transition_to(PlayingState())
