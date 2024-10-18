import logging
from typing import Iterable, Iterator, Optional
from enum import StrEnum

import re
import httpx
import yt_dlp
from yt_dlp import YoutubeDL

from pipo.config import settings
from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType


try:
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    HTTPXClientInstrumentor().instrument()
except ImportError:
    logging.getLogger(__name__).warning("Unable to import HTTPXClientInstrumentor")


class YoutubeOperations(StrEnum):
    """Youtube operation types."""

    URL = "url"
    PLAYLIST = "playlist"
    QUERY = "query"


class YoutubeHandler(BaseHandler):
    """Handles youtube url music."""

    name = SourceType.YOUTUBE

    @staticmethod
    def __valid_source(source: Iterable[str]) -> bool:
        """Check whether source is a youtube url."""
        return source and ("youtube" in source and source.startswith(("https", "http")))
        return source and ("youtube" in source and source.startswith(("https", "http")))

    def handle(self, source: str) -> SourcePair:
        if self.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube audio source '%s'", source
            )
            if "list=" in source:
                return SourcePair(
                    query=source,
                    handler_type=YoutubeHandler.name,
                    operation=YoutubeOperations.PLAYLIST,
                )
            else:
                return SourcePair(
                    query=source,
                    handler_type=YoutubeHandler.name,
                    operation=YoutubeOperations.URL,
                )
        else:
            return super().handle(source)

    @staticmethod
    def parse_playlist(url: str) -> Iterator[str]:
        try:
            with YoutubeDL(
                settings.player.source.youtube.playlist_parser_config
            ) as ydl:
                playlist_id = ydl.extract_info(url=url, download=False).get("id")
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                for url in ydl.extract_info(url=playlist_url, download=False).get(
                    "entries"
                ):
                    yield url.get("url")
        except yt_dlp.utils.DownloadError:
            logging.getLogger(__name__).exception(
                "Unable to obtain information from youtube"
            )

    @staticmethod
    def get_audio(query: str) -> Optional[str]:
        """Obtain a youtube audio url.

        Given a query or a youtube url obtains the best quality audio url.
        Retries fetching audio url in case of error waiting between attempts.

        Parameters
        ----------
        query : str
            Youtube video url or query.

        Returns
        -------
        Optional[str]
            Youtube audio url or None if no audio url was found.
        """
        logging.getLogger(__name__).debug(
            "Trying to obtain youtube audio url %s", query
        )
        url = None
        if query:
            logging.getLogger(__name__).debug(
                "Attempting to obtain youtube audio url %s", query
            )
            try:
                with YoutubeDL(settings.player.source.youtube.downloader_config) as ydl:
                    url = ydl.extract_info(url=query, download=False).get("url", None)
            except Exception:
                logging.getLogger(__name__).warning(
                    "Unable to obtain audio url %s",
                    query,
                    exc_info=True,
                )
            if url:
                logging.getLogger(__name__).info(
                    "Obtained audio url for query '%s'", query
                )
                return url
        logging.getLogger(__name__).warning("Unable to obtain audio url %s", query)
        return None


class YoutubeQueryHandler(BaseHandler):
    """Youtube query handler.

    Handles youtube search queries. Exposes no accept condition therefore should only be
    used as terminal handler.
    """

    name = SourceType.YOUTUBE

    @staticmethod
    def __valid_source(source: str) -> bool:
        """Check whether source is an url."""
        return source and (not source.startswith(("https", "http")))

    def handle(self, source: str) -> SourcePair:
        if self.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube query audio source '%s'", source
            )
            return SourcePair(
                query=source,
                handler_type=SourceType.YOUTUBE,
                operation=YoutubeOperations.QUERY,
            )
        else:
            return super().handle(source)

    @staticmethod
    async def url_from_query(query: str) -> Optional[str]:
        """Get youtube audio url based on search query.

        Perform a youtube query to obtain the related video with the most views.

        Parameters
        ----------
        query : str
            Word query to search.

        Returns
        -------
        Optional[str]
            Youtube video url best matching query, None if no video found.
        """
        url = None
        if query:
            query = query.replace(" ", "+").encode("ascii", "ignore").decode()
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"https://www.youtube.com/results?search_query={query}",
                        timeout=settings.player.url_fetch.timeout,
                    )
                    video_id = re.search(r"watch\?v=(\S{11})", response.text).group(1)
                    url = (
                        f"https://www.youtube.com/watch?v={video_id}"
                        if video_id
                        else None
                    )
                except httpx.TimeoutException:
                    logging.getLogger(__name__).exception("Unable to search for query")
        return url
