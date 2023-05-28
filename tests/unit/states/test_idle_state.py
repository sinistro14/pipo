#!usr/bin/env python3

import asyncio

import mock
import pytest

import tests.constants
from pipo.states.idle_state import IdleState


class TestIdleState:

    __state_name = "idle"

    def teardown(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()  # returns after calling loop.stop()
            tasks = asyncio.Task.all_tasks()
            for t in [t for t in tasks if not (t.done() or t.cancelled())]:
                loop.run_until_complete(t)
        finally:
            loop.close()

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
        assert state.name == "disconnected"

    @pytest.mark.asyncio
    async def test_play(self, state: IdleState):
        assert state.name == self.__state_name
        await state.play(None, ["test"], True)
        assert state.name == "playing"

    @pytest.mark.asyncio
    async def test_resume(self, state: IdleState):
        state.name == self.__state_name
        await state.resume()
        assert state.name == "playing"

    @pytest.mark.asyncio
    async def test_leave(self, state: IdleState):
        state.name == self.__state_name
        await state.leave()
        assert state.name == "disconnected"
