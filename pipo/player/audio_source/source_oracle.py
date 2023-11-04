from typing import Iterable

from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler


class SourceOracle:
    @staticmethod
    def __handlers() -> BaseHandler:
        """Provide handler chain."""
        handlers = YoutubeHandler()
        handlers.set_next(YoutubeQueryHandler())
        return handlers

    @staticmethod
    def get_sources(
        queries: Iterable[str] = (),
        source_type: str = "",
    ) -> Iterable[SourcePair]:
        handlers = SourceOracle.__handlers()
        sources = [handlers.handle(query) for query in queries]
        return [item for item in sources if item is not None]
