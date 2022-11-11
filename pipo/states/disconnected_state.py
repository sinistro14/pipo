from pipo.states.idle_state import IdleState
from pipo.states.playing_state import PlayingState
from pipo.states.state import State


class DisconnectedState(State):
    def join(self) -> None:
        self.context.join()
        self.context.transition_to(IdleState())

    def play(self) -> None:
        self.context.joinAndPlay()
        self.context.transition_to(PlayingState())

    def playlist(self) -> None:
        self.context.joinAndPlayList()
        self.context.transition_to(PlayingState())
