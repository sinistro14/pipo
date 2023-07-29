import asyncio
import logging
from abc import ABC, abstractmethod


class Command(ABC):
    """Abstract Command."""

    _logger: logging.Logger

    def __init__(self) -> None:
        logging.getLogger(__name__)

    async def execute(self) -> None:
        """Command execution method.

        Calls subclass defined _execute method, handling task cancellation logic.
        """
        try:
            await self._execute()
        except asyncio.CancelledError:
            self._logger.info("Cancelling command", exc_info=True)
        except Exception:
            self._logger.exception("Unable to execute command")

    @abstractmethod
    async def _execute(self) -> None:
        """Subclass specific execution method."""
        pass
