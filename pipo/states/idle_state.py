import asyncio

from .state import State
from pipo.states.playing_state import PlayingState
from pipo.states.disconnected_state import DisconnectedState

class IdleState(State):

    _idle_counter = None
    _idle_duration: int = 60 * 30  ## 30 min

    def __init__(self) -> None:
        super().__init__()
        self._start_idle_counter()

    def _start_idle_counter(self):
        self._idle_counter = asyncio.ensure_future(self._idle_time_task())

    def _stop_idle_counter(self):
        if self._idle_counter:
            self.idle_counter.cancel()
            self.idle_counter = None

    async def _idle_time_task(self):
        await asyncio.sleep(self._idle_duration)
        self.context.transition_to(DisconnectedState())
        await self.context.musicChannel.send("Bye Bye !!!")
        await self.context.voiceClient.disconnect()
    
    def _clean_transition_to(self, state: State):
        self._stop_idle_counter()
        self.context.transition_to(state)

    def play(self) -> None:
        #self.play
        self._clean_transition_to(PlayingState())

    def playlist(self) -> None:
        #self.playList
        self._clean_transition_to(PlayingState())

    def leave(self) -> None:
        #self.leave
        self._clean_transition_to(DisconnectedState())

    def resume(self) -> None:
        #self.resume
        self._clean_transition_to(PlayingState())
