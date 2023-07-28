import logging
from abc import ABC, abstractmethod
from typing import List

from discord.ext.commands import Context as Dctx


class Context:

    _state = None
    _logger: logging.Logger

    def __init__(self, state) -> None:
        self._logger = logging.getLogger(__name__)
        self.transition_to(state)

    def transition_to(self, state):
        self._state = state
        self._state.context = self
        self._logger.info("Current State", extra=dict(state=self._state.name))


class State(ABC):
    """State machine base.

    Declares methods all concrete State should
    implement and provides a reference to the associated Context object,
    which can be used by States to transition Context to another State.
    """

    name: str
    _context: Context
    _logger: logging.Logger

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(__name__)
        self.name = name

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    async def join(self, ctx: Dctx) -> None:
        pass

    @abstractmethod
    async def play(self, ctx: Dctx, query: List[str], shuffle: bool) -> None:
        pass

    @abstractmethod
    async def skip(self) -> None:
        pass

    @abstractmethod
    async def leave(self) -> None:
        pass

    @abstractmethod
    async def resume(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def pause(self) -> None:
        pass
