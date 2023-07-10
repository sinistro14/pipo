import asyncio
import logging

from pipo.command.command import Command


class CommandQueue:

    __command_executor: asyncio.AbstractEventLoop

    def __init__(self, loop: asyncio.AbstractEventLoop = None) -> None:
        self._logger = logging.getLogger(__name__)
        #self.__command_executor = loop or asyncio.get_running_loop()

    async def add(self, command: Command) -> asyncio.Task:
        await asyncio.create_task(command.execute())

    def stop(self) -> None:
        pass
        #self.__command_executor.stop()
