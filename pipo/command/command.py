import asyncio
import logging
from abc import ABC, abstractmethod


class Command(ABC):

    _logger: logging.Logger

    def __init__(self) -> None:
        logging.getLogger(__name__)

    async def execute(self) -> None:
        try:
            await self._execute()
        except asyncio.CancelledError:
            self._logger.info("Cancelling command.")

    @abstractmethod
    async def _execute(self) -> None:
        pass
