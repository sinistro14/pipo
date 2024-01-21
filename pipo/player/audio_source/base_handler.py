from abc import abstractmethod
from typing import Iterable, Optional

from pipo.player.audio_source.source_handler import SourceHandler
from pipo.player.audio_source.source_pair import SourcePair


class BaseHandler(SourceHandler):
    """Defines handler default behavior."""

    _next_handler: SourceHandler = None

    def set_next(self, handler: SourceHandler) -> SourceHandler:
        """Define next handler."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, source: str) -> SourcePair:
        """Check whether handler is able to process source."""
        if self._next_handler:
            return self._next_handler.handle(source)
        return None

    @staticmethod
    def parse(sources: SourcePair) -> Iterable[SourcePair]:
        """Process requests that may encompass several musics."""
        return [sources]

    @staticmethod
    @abstractmethod
    def fetch(source: str) -> Optional[str]:
        """Fetch resources from source."""
        return None
