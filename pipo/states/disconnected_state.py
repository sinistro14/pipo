from .state import State
from pipo.states.idle_state import IdleState
from pipo.states.playing_state import PlayingState

class DisconnectedState(State):

    def join(self) -> None:
        self.join
        self.context.transition_to(IdleState())

    def play(self) -> None:
        self.joinAndPlay
        self.context.transition_to(PlayingState())

    def playlist(self) -> None:
        self.joinAndPlayList
        self.context.transition_to(PlayingState())
