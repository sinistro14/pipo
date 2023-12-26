import logging
import time
from typing import Iterable, Optional

from yt_dlp import YoutubeDL

from pipo.config import settings
from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType


class YoutubeHandler(BaseHandler):
    """Handles youtube url music."""

    name = SourceType.YOUTUBE

    @staticmethod
    def __valid_source(source: Iterable[str]) -> bool:
        return source and ("youtube" in source and source.startswith(("http", "https")))

    def handle(self, source: str) -> SourcePair:
        if self.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube audio source %s", source
            )
            return SourcePair(query=source, handler_type=YoutubeHandler.name)
        else:
            return super().handle(source)

    @staticmethod
    def parse(pair: SourcePair) -> Iterable[SourcePair]:
        query = pair.query
        if "list=" in query:  # check if playlist
            with YoutubeDL({"extract_flat": True}) as ydl:
                playlist_id = ydl.extract_info(url=query, download=False).get("id")
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                audio = [
                    url.get("url")
                    for url in ydl.extract_info(url=playlist_url, download=False).get(
                        "entries"
                    )
                ]
                parsed_query = [
                    SourcePair(entry, YoutubeHandler.name) for entry in audio
                ]
        else:
            parsed_query = [  # noqa
                SourcePair(query, YoutubeHandler.name),
            ]
        return parsed_query

    @staticmethod
    def fetch(source: str) -> Optional[str]:
        if YoutubeHandler.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube audio source %s", source
            )
            return YoutubeHandler.get_audio(source)
        return None

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
            for attempt in range(settings.player.url_fetch.retries):
                logging.getLogger(__name__).debug(
                    "Attempt %s to obtain youtube audio url %s", attempt, query
                )
                try:
                    with YoutubeDL({"format": "bestaudio/best"}) as ydl:
                        url = ydl.extract_info(url=query, download=False).get(
                            "url", None
                        )
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
                time.sleep(settings.player.url_fetch.wait)
        logging.getLogger(__name__).warning("Unable to obtain audio url %s", query)
        return None
