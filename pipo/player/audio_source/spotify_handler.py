import logging
from typing import Iterable

import spotipy

from pipo.config import settings
from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler


class SpotifyHandler(BaseHandler):
    """Handles spotify url music."""

    name = SourceType.SPOTIFY

    @staticmethod
    def __valid_source(source: Iterable[str]) -> bool:
        """Check whether source is a spotify url."""
        return source and ("spotify" in source and source.startswith(("https", "http")))

    def handle(self, source: str) -> SourcePair:
        if self.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing spotify audio source '%s'", source
            )
            return SourcePair(query=source, handler_type=SpotifyHandler.name)
        else:
            return super().handle(source)

    @staticmethod
    def parse(pair: SourcePair) -> Iterable[SourcePair]:
        query = pair.query
        spotify = spotipy.Spotify()
        # TODO handle exceptions
        if "playlist" in query:
            logging.getLogger(__name__).info("Processing spotify playlist '%s'", query)
            tracks = spotify.playlist_tracks(
                query,
                fields=["name", "artists"],
                limit=settings.player.source.spotify.playlist_limit,
            )
        elif "album" in query:
            logging.getLogger(__name__).info("Processing spotify album '%s'", query)
            tracks = spotify.album_tracks(
                query, limit=settings.player.source.spotify.album_limit
            )
        else:
            logging.getLogger(__name__).info("Processing spotify track '%s'", query)
            tracks = [spotify.track(query)]
        parsed_query = []
        for track in tracks:
            song = track["name"]
            artist = track["artists"][0] if track["artists"] else ""
            entry = f"{song} - {artist}" if artist else song
            parsed_query.append(SourcePair(entry, YoutubeQueryHandler.name))
        return parsed_query
