class Context:

    _state = None

    def __init__(self, state) -> None:
        self.transition_to(state) # initial state

    def transition_to(self, state):
        self._state = state
        self._state.context = self
