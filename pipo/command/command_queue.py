import asyncio
import logging
from typing import Set

from pipo.command.command import Command


class CommandQueue:

    _logger: logging.Logger
    __scheduled_tasks: Set[asyncio.Task]

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self.__scheduled_tasks = set()

    async def add(self, command: Command) -> asyncio.Task:
        task = asyncio.create_task(command.execute())
        self.__scheduled_tasks.add(task)
        task.add_done_callback(self.__scheduled_tasks.discard)

    def stop(self) -> None:
        for task in self.__scheduled_tasks:
            task.cancel()
