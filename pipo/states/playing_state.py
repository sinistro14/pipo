from pipo.states.disconnected_state import DisconnectedState
from pipo.states.idle_state import IdleState
from pipo.states.state import State


class PlayingState(State):
    def stop(self) -> None:
        self.context.stop()
        self.context.transition_to(IdleState())

    def pause(self) -> None:
        self.context.pause()
        self.context.transition_to(IdleState())

    def leave(self) -> None:
        self.context.leave()
        self.context.transition_to(DisconnectedState())

    def play(self) -> None:
        self.context.play()

    def playlist(self) -> None:
        self.context.playlist()

    def skip(self) -> None:
        self.context.skip()

    def skiplist(self) -> None:
        self.context.skiplist()
