from typing import Iterable, Optional

from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType


class NullHandler(BaseHandler):
    """Handles youtube url music."""

    name = SourceType.NULL

    def handle(self, source: Iterable[str]) -> SourcePair:
        return SourcePair(query=source, handler_type=NullHandler.name)

    @staticmethod
    def fetch(source: str) -> Optional[str]:
        return None
