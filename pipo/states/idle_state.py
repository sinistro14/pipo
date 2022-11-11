import asyncio

from pipo.states.disconnected_state import DisconnectedState
from pipo.states.playing_state import PlayingState
from pipo.states.state import State


class IdleState(State):

    _idle_tracker = None
    _idle_timeout: int = 0

    def __init__(self, idle_timeout: int = 60 * 30) -> None:  # 30 minutes
        super().__init__()
        self._idle_timeout = idle_timeout
        self._start_idle_tracker()

    def _start_idle_tracker(self):
        self._idle_tracker = asyncio.ensure_future(self._idle_tracker_task())

    def _stop_idle_tracker(self):
        if self._idle_tracker:
            self.idle_counter.cancel()
            self.idle_counter = None

    async def _idle_tracker_task(self):
        await asyncio.sleep(self._idle_timeout)
        self.context.transition_to(DisconnectedState())
        await self.context.musicChannel.send("Bye Bye !!!")
        await self.context.voiceClient.disconnect()

    def _clean_transition_to(self, state: State):
        self._stop_idle_tracker()
        self.context.transition_to(state)

    def play(self) -> None:
        self.context.play()
        self._clean_transition_to(PlayingState())

    def playlist(self) -> None:
        self.context.playList()
        self._clean_transition_to(PlayingState())

    def leave(self) -> None:
        self.context.leave()
        self._clean_transition_to(DisconnectedState())

    def resume(self) -> None:
        self.context.resume()
        self._clean_transition_to(PlayingState())
