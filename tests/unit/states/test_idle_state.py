#!usr/bin/env python3
import asyncio

import mock
import pytest

import tests.constants
from pipo.states.idle_state import IdleState
from pipo.states.playing_state import PlayingState
from pipo.states.disconnected_state import DisconnectedState


class TestIdleState:

    __state_name = "idle"

    @pytest.fixture(scope="function")
    def initial_state(self, mocker) -> IdleState:
        mocker.patch("pipo.states.idle_state.IdleState.context", new=mock.AsyncMock())
        return IdleState(tests.constants.IDLE_TIMEOUT)

    @pytest.mark.asyncio
    async def test_disabled_commands(self, initial_state: IdleState):
        await initial_state.join(None)
        await initial_state.skip()
        await initial_state.pause()
        await initial_state.clear()

    @pytest.mark.asyncio
    async def test_idle_timeout(self, initial_state: IdleState):
        assert initial_state.name == self.__state_name
        await asyncio.sleep(tests.constants.IDLE_TIMEOUT + 1)
        assert len(initial_state.context.transition_to.call_args.args) == 1
        next_state = initial_state.context.transition_to.call_args.args[0]
        assert next_state.name == DisconnectedState().name

    @pytest.mark.parametrize(
        "method, args, final_state",
        [
            ("play", (None, ["test"], True), PlayingState),
            ("resume", (), PlayingState),
            ("leave", (), DisconnectedState),
        ],
    )
    @pytest.mark.asyncio
    async def test_state_transition(
        self, initial_state: IdleState, method, args, final_state
    ):
        initial_state.name == self.__state_name
        await getattr(initial_state, method)(*args)
        assert len(initial_state.context.transition_to.call_args.args) == 1
        result_state = initial_state.context.transition_to.call_args.args[0]
        assert result_state.name == final_state().name
