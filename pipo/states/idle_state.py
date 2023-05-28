import asyncio
from typing import List

from discord.ext.commands import Context as Dctx

import pipo.states.state
import pipo.states.playing_state
import pipo.states.disconnected_state
from pipo.config import settings


class IdleState(pipo.states.state.State):
    """Time aware idle state.

    State allowing play, resume and leave functionality.
    After initialization starts an internal timeout for migration to Disconnected state.
    """

    _idle_timeout: int
    _idle_tracker: asyncio.Future

    def __init__(self, idle_timeout: int = settings.player.idle_timeout):
        super().__init__("idle")
        self._idle_timeout = idle_timeout
        self._start_idle_tracker()

    def _start_idle_tracker(self):
        self._idle_tracker = asyncio.ensure_future(
            self._idle_tracker_task(), loop=asyncio.get_event_loop()
        )

    def _stop_idle_tracker(self):
        if self._idle_tracker:
            self._idle_tracker.cancel()
            self._idle_tracker = None

    async def _idle_tracker_task(self):
        await asyncio.sleep(self._idle_timeout)
        self.context.transition_to(pipo.states.disconnected_state.DisconnectedState())
        await self.context._music_channel.send(settings.player.messages.disconnect)
        await self.context._voice_client.disconnect()

    def _clean_transition_to(self, state: pipo.states.state.State) -> None:
        self._stop_idle_tracker()
        self.context.transition_to(state)

    async def join(self, ctx: Dctx) -> None:
        pass

    async def skip(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def pause(self) -> None:
        pass

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        self.context._player.play(query, shuffle)
        self._clean_transition_to(pipo.states.playing_state.PlayingState())

    async def leave(self) -> None:
        await self.context._voice_client.disconnect()
        self.context.transition_to(pipo.states.disconnected_state.DisconnectedState())

    async def resume(self) -> None:
        self.context._player.resume()
        self._clean_transition_to(pipo.states.playing_state.PlayingState())
