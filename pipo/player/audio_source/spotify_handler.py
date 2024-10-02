import asyncio
from enum import StrEnum
import logging
import random
from typing import Iterable, Iterator, List

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


class SpotifyOperations(StrEnum):
    """Spotify operation types."""

    URL = "url"


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
            return SourcePair(
                query=source, handler_type=SpotifyHandler.name, operation="url"
            )
        else:
            return super().handle(source)

    @staticmethod
    def __format_query(track: SpotifyTrack) -> SourcePair:
        song = track.name
        artist = track.artists[0].name if track.artists else ""
        entry = f"{song} - {artist}" if artist else song
        return SourcePair(
            query=entry,
            handler_type=YoutubeQueryHandler.name,
        )

    @staticmethod
    def _get_playlist(
        client: spotipy.Spotify, query: str, fields: Iterable[str], limit: int
    ) -> List[SpotifyTrack]:
        tracks = client.playlist_items(
            query,
            fields=fields,
            limit=limit,
            additional_types="track",
        )
        return SpotifyPlaylist(**tracks).items

    @staticmethod
    def _get_album(
        client: spotipy.Spotify, query: str, limit: int
    ) -> List[SpotifyTrack]:
        tracks = client.album_tracks(
            query,
            limit=limit,
        )
        return SpotifyAlbum(**tracks).items

    @staticmethod
    def _get_track(client: spotipy.Spotify, query: str) -> List[SpotifyTrack]:
        track = client.track(
            query,
        )
        return [SpotifyTrack(**track)]

    @staticmethod
    async def tracks_from_query(
        query: str, shuffle: bool = False
    ) -> Iterable[SourcePair]:
        """
        TODO

        asyncio.to_thread is used to avoid blocking asyncio event loop, considering Spotipy
        library is not CPU nor asyncio friendly.
        """
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
                task = asyncio.to_thread(
                    SpotifyHandler._get_playlist,
                    spotify,
                    query,
                    [settings.player.source.spotify.playlist.filter],
                    settings.player.source.spotify.playlist.limit,
                )
            elif "album" in query:
                logging.getLogger(__name__).info("Processing spotify album '%s'", query)
                task = asyncio.to_thread(
                    SpotifyHandler._get_album,
                    spotify,
                    query,
                    settings.player.source.spotify.album.limit,
                )
            else:
                logging.getLogger(__name__).info("Processing spotify track '%s'", query)
                task = asyncio.to_thread(SpotifyHandler._get_track, spotify, query)
            tracks = (await asyncio.gather(task))[0]
        except spotipy.oauth2.SpotifyOauthError:
            logging.getLogger(__name__).exception(
                "Unable to access spotify API. \
                Confirm API credentials are correct."
            )
        except spotipy.exceptions.SpotifyException:
            logging.getLogger(__name__).exception(
                "Unable to process spotify query '%s'", query
            )
        if shuffle:
            random.shuffle(tracks)
        return [SpotifyHandler.__format_query(track) for track in tracks]
