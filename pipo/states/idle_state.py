import asyncio
from typing import List

from discord.ext.commands import Context as Dctx

import pipo.states.disconnected_state
import pipo.states.playing_state
import pipo.states.state
from pipo.config import settings


class IdleState(pipo.states.state.State):
    """Bot idle state.

    Starts an internal timeout for migration to Disconnected state.
    Cancelled if a play command is received.
    Can process commands:
        * :meth:`play`
        * :meth:`leave`
        * :meth:`resume`

    Attributes
    ----------
    _idle_timeout : int
        Time in seconds before timeout.
    idle_tracker : asyncio.Future
        Task tracking passed time.
    cancel_event : asyncio.Event
        Event blocking transition to Disconnected until :attr:`idle_tracker` timeout.
    """

    _idle_timeout: int
    idle_tracker: asyncio.Future
    cancel_event: asyncio.Event

    def __init__(self, idle_timeout: int = settings.player.idle.timeout):
        super().__init__("idle")
        self._idle_timeout = idle_timeout
        self.cancel_event = asyncio.Event()
        self._start_idle_tracker()

    def _start_idle_tracker(self):
        """Initialize idle timeout tracker."""
        self.idle_tracker = asyncio.create_task(
            self._idle_tracker_task(self.cancel_event),
            name=settings.player.idle.task_name,
        )

    async def _stop_idle_tracker(self):
        """Stop idle timeout tracker."""
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
            self._logger.debug("Cancelling task 'idle_tracker'")

    async def _clean_transition_to(self, state: pipo.states.state.State) -> None:
        """Orderly transition to a new state.

        Ensures idle timeout tracker is stopped before transitioning to new state.
        """
        await self._stop_idle_tracker()
        self.context.transition_to(state)

    async def join(self, ctx: Dctx) -> None:  # noqa: D102
        pass

    async def skip(self) -> None:  # noqa: D102
        pass

    async def clear(self) -> None:  # noqa: D102
        pass

    async def pause(self) -> None:  # noqa: D102
        pass

    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        """Add music to play.

        Add music and transition to Playing State.

        Parameters
        ----------
        ctx : Dctx
            Bot context.
        query : List[str]
            Music to play.
        shuffle : bool, optional
            Randomize play order when multiple musics are provided.
        """
        self.context.player.play(query, shuffle)
        await self._clean_transition_to(pipo.states.playing_state.PlayingState())

    async def leave(self) -> None:
        """Make bot leave the current server.

        Bot leaves server and transition to Disconnected State.
        """
        await self.context.voice_client.disconnect()
        self.context.transition_to(pipo.states.disconnected_state.DisconnectedState())

    async def resume(self) -> None:
        """Resume previously paused music.

        Resume music and transition to Playing State.
        """
        self.context.player.resume()
        await self._clean_transition_to(pipo.states.playing_state.PlayingState())
