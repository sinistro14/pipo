import logging
from typing import Iterable

import spotipy

from pipo.config import settings
from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.schemas.spotify import (
    SpotifyAlbum,
    SpotifyPlaylist,
    SpotifyTrack,
)
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType
from pipo.player.audio_source.youtube_handler import YoutubeQueryHandler


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
    def __format_query(track: SpotifyTrack) -> SourcePair:
        song = track.name
        artist = track.artists[0].name if track.artists else ""
        entry = f"{song} - {artist}" if artist else song
        return SourcePair(
            query=entry, handler_type=YoutubeQueryHandler.name, operation="query"
        )

    @staticmethod
    def tracks_from_query(query: str) -> Iterable[SourcePair]:
        tracks = []
        try:
            spotify = spotipy.Spotify(
                client_credentials_manager=spotipy.SpotifyClientCredentials(
                    client_id=settings.spotify_client,
                    client_secret=settings.spotify_secret,
                )
            )
            if "playlist" in query:
                logging.getLogger(__name__).info(
                    "Processing spotify playlist '%s'", query
                )
                tracks = spotify.playlist_items(
                    query,
                    fields=[settings.player.source.spotify.playlist.filter],
                    limit=settings.player.source.spotify.playlist.limit,
                )
                tracks = SpotifyPlaylist(**tracks).items
            elif "album" in query:
                logging.getLogger(__name__).info("Processing spotify album '%s'", query)
                tracks = spotify.album_tracks(
                    query,
                    limit=settings.player.source.spotify.album.limit,
                )
                tracks = SpotifyAlbum(**tracks).items
            else:
                logging.getLogger(__name__).info("Processing spotify track '%s'", query)
                track = spotify.track(query)
                tracks = [SpotifyTrack(**track)]
        except spotipy.oauth2.SpotifyOauthError:
            logging.getLogger(__name__).exception(
                "Unable to access spotify API. \
                Confirm API credentials are correct."
            )
        except spotipy.exceptions.SpotifyException:
            logging.getLogger(__name__).exception(
                "Unable to process spotify query '%s'", query
            )
        return [SpotifyHandler.__format_query(track) for track in tracks]
