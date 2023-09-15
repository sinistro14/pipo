import logging
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from pipo.player.audio_source.source_pair import SourcePair


class SourceHandler(ABC):
    """Base source handler.

    Declares a method for building the chain of handlers.
    Also declares a method for executing a request.
    """

    name: str
    _logger: logging.Logger
    # TODO implement caching solution

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def set_next(self, handler):
        pass

    @abstractmethod
    def handle(self, source: Iterable[str]) -> SourcePair:
        pass

    @abstractmethod
    def fetch(self, source: str) -> Optional[str]:
        pass
