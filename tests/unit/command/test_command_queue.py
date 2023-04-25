#!usr/bin/env python3
import pytest

import pipo.command.command
import pipo.command.command_queue
from pipo.config import settings


class DummyCommand(pipo.command.command.Command):
    def execute(self) -> None:
        return 0


class TestCommandQueue:
    @pytest.fixture(scope="function")
    def command_queue(self):
        return pipo.command.command_queue.CommandQueue(
            settings.command.queue.max_workers
        )

    def test_add_command(self, command_queue: pipo.command.command_queue.CommandQueue):
        command = DummyCommand()
        command_queue.add(command)
