from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.null_handler import NullHandler
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler


class SourceFactory:
    @staticmethod
    def get_source(source_type: str) -> BaseHandler:
        handlers = (
            YoutubeHandler,
            YoutubeQueryHandler,
            NullHandler,
        )
        return {handler.name: handler for handler in handlers}.get(
            source_type, NullHandler.name
        )
