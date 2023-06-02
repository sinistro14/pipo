#!usr/bin/env python3

import asyncio

import mock
import pytest

import tests.constants
from pipo.states.idle_state import IdleState


class TestIdleState:

    __state_name = "idle"

    @pytest.fixture(scope="function")
    def state(self, mocker) -> IdleState:
        mocker.patch("pipo.states.idle_state.IdleState.context", new=mock.AsyncMock())
        return IdleState(tests.constants.IDLE_TIMEOUT)

    @pytest.mark.asyncio
    async def test_disabled_commands(self, state: IdleState):
        await state.join(None)
        await state.skip()
        await state.pause()
        await state.stop()

    @pytest.mark.asyncio
    async def test_timeout(self, state: IdleState):
        assert state.name == self.__state_name
        await asyncio.sleep(tests.constants.IDLE_TIMEOUT + 1)
        assert len(state.context.transition_to.call_args.args) == 1
        next_state = state.context.transition_to.call_args.args[0]
        assert next_state.name == "disconnected"

    @pytest.mark.asyncio
    async def test_play(self, state: IdleState):
        assert state.name == self.__state_name
        await state.play(None, ["test"], True)
        assert len(state.context.transition_to.call_args.args) == 1
        next_state = state.context.transition_to.call_args.args[0]
        assert next_state.name == "playing"

    @pytest.mark.asyncio
    async def test_resume(self, state: IdleState):
        state.name == self.__state_name
        await state.resume()
        assert len(state.context.transition_to.call_args.args) == 1
        next_state = state.context.transition_to.call_args.args[0]
        assert next_state.name == "playing"

    @pytest.mark.asyncio
    async def test_leave(self, state: IdleState):
        state.name == self.__state_name
        await state.leave()
        assert len(state.context.transition_to.call_args.args) == 1
        next_state = state.context.transition_to.call_args.args[0]
        assert next_state.name == "disconnected"
