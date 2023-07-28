import asyncio
from typing import List

from discord.ext.commands import Context as Dctx

import pipo.states.disconnected_state
import pipo.states.playing_state
import pipo.states.state
from pipo.config import settings


class IdleState(pipo.states.state.State):
    """Time aware idle state.

    State allowing play, resume and leave functionality.
    After initialization starts an internal timeout for migration to Disconnected state.
    """

    _idle_timeout: int
    idle_tracker: asyncio.Future
    cancel_event: asyncio.Event

    def __init__(self, idle_timeout: int = settings.player.idle_timeout):
        super().__init__("idle")
        self._idle_timeout = idle_timeout
        self.cancel_event = asyncio.Event()
        self._start_idle_tracker()

    def _start_idle_tracker(self):
        self.idle_tracker = asyncio.ensure_future(
            self._idle_tracker_task(self.cancel_event)
        )

    async def _stop_idle_tracker(self):
        if self.idle_tracker:
            self.cancel_event.set()
            await self.idle_tracker
            self.idle_tracker = None

    async def _idle_tracker_task(self, cancel_event: asyncio.Event):
        try:
            await asyncio.wait_for(cancel_event.wait(), timeout=self._idle_timeout)
        except asyncio.TimeoutError:
            self.context.transition_to(
                pipo.states.disconnected_state.DisconnectedState()
            )
            await self.context.music_channel.send(settings.player.messages.disconnect)
            await self.context.voice_client.disconnect()
        except asyncio.CancelledError:
            self._logger.info("Cancelling idle tracker task", exc_info=True)

    async def _clean_transition_to(self, state: pipo.states.state.State) -> None:
        await self._stop_idle_tracker()
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
        self.context.player.play(query, shuffle)
        await self._clean_transition_to(pipo.states.playing_state.PlayingState())

    async def leave(self) -> None:
        await self.context.voice_client.disconnect()
        self.context.transition_to(pipo.states.disconnected_state.DisconnectedState())

    async def resume(self) -> None:
        self.context.player.resume()
        await self._clean_transition_to(pipo.states.playing_state.PlayingState())
