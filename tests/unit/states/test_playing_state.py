#!usr/bin/env python3

import mock
import pytest

from pipo.states.idle_state import IdleState
from pipo.states.playing_state import PlayingState
from pipo.states.disconnected_state import DisconnectedState


class TestPlayingState:

    __state_name = "playing"

    @pytest.fixture(scope="function")
    def initial_state(self, mocker) -> PlayingState:
        mocker.patch(
            "pipo.states.playing_state.PlayingState.context", new=mock.AsyncMock()
        )
        return PlayingState()

    @pytest.mark.asyncio
    async def test_disabled_commands(self, initial_state: PlayingState):
        await initial_state.join(None)
        await initial_state.resume()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method, args, final_state",
        [
            ("stop", (), IdleState),
            ("pause", (), IdleState),
            ("leave", (), DisconnectedState),
            # ("play", (None, ["test"], True), PlayingState),
        ],
    )
    async def test_state_transition(
        self, initial_state: PlayingState, method, args, final_state
    ):
        initial_state.name == self.__state_name
        await getattr(initial_state, method)(*args)
        assert len(initial_state.context.transition_to.call_args.args) == 1
        result_state = initial_state.context.transition_to.call_args.args[0]
        assert result_state.name == final_state().name
