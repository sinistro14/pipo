from .state import State
from pipo.states.idle_state import IdleState
from pipo.states.disconnected_state import DisconnectedState

class PlayingState(State):

    def stop(self) -> None:
        self.stop
        self.context.transition_to(IdleState())

    def pause(self) -> None:
        self.pause
        self.context.transition_to(IdleState())
    
    def leave(self) -> None:
        self.leave
        self.context.transition_to(DisconnectedState())
    
    def play(self) -> None:
        self.play
        
    def playlist(self) -> None:
        self.playlist

    def skip(self) -> None:
        self.skip

    def skiplist(self) -> None:
        self.skiplist
