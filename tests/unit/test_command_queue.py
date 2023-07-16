#!usr/bin/env python3
import asyncio

import pytest

import pipo.command.command
import pipo.command.command_queue


class DummyCommand(pipo.command.command.Command):
    async def _execute(self):
        return 0


class DummyAsyncCommand(pipo.command.command.Command):
    event: asyncio.Event

    def __init__(self, event) -> None:
        self.event = event

    async def _execute(self):
        self.event.set()


class TestCommandQueue:
    @pytest.fixture(scope="function")
    def command_queue(self):
        return pipo.command.command_queue.CommandQueue()

    def test_add_command(self, command_queue: pipo.command.command_queue.CommandQueue):
        command = DummyCommand()
        command_queue.add(command)

    @pytest.mark.asyncio
    async def test_add_async_command(
        self, command_queue: pipo.command.command_queue.CommandQueue
    ):
        event = asyncio.Event()
        command = DummyAsyncCommand(event)
        await command_queue.add(command)
        await event.wait()
        assert event.is_set()
