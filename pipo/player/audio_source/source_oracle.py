from typing import Iterable

from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler


class SourceOracle:
    """Based on received queries provides the most appropriate source handlers."""

    @staticmethod
    def __handlers() -> BaseHandler:
        """Provide handler chain."""
        handlers = YoutubeHandler()
        handlers.set_next(YoutubeQueryHandler())
        return handlers

    @staticmethod
    def process_queries(
        queries: Iterable[str],
    ) -> Iterable[SourcePair]:
        """Match queries with most fitting handlers.

        Parameters
        ----------
        queries : Iterable[str]
            Queries to process.

        Returns
        -------
        Iterable[SourcePair]
            Based on queries provides the most appropriate source handler pairs.
        """
        handlers = SourceOracle.__handlers()
        sources = [handlers.handle(query) for query in queries]
        return [item for item in sources if item is not None]
