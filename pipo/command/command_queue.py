import asyncio
import logging

from pipo.command.command import Command


class CommandQueue:

    __command_executor: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self.__command_executor = asyncio.get_event_loop()

    def add(self, command: Command) -> asyncio.Task:
        return self.__command_executor.create_task(command.execute())

    def stop(self) -> None:
        self.__command_executor.stop()
