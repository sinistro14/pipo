import logging
import re
from typing import Optional

import requests

from pipo.config import settings
from pipo.player.audio_source.base_handler import BaseHandler
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType
from pipo.player.audio_source.youtube_handler import YoutubeHandler


class YoutubeQueryHandler(BaseHandler):
    """Youtube query handler.

    Handles youtube search queries. Exposes no accept condition therefore should only be
    used as terminal handler.
    """

    name = SourceType.YOUTUBE_QUERY

    @staticmethod
    def __valid_source(source: str) -> bool:
        return source and (not source.startswith(("http", "https")))

    def handle(self, source: str) -> SourcePair:
        if self.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube query audio source '%s'", source
            )
            return SourcePair(query=source, handler_type=YoutubeQueryHandler.name)
        else:
            return super().handle(source)

    @staticmethod
    def fetch(source: str) -> Optional[str]:
        if YoutubeQueryHandler.__valid_source(source):
            logging.getLogger(__name__).info(
                "Processing youtube audio query source '%s'", source
            )
            return YoutubeQueryHandler.get_audio(source)
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
        url = YoutubeQueryHandler._music_from_query(query)
        if url:
            return YoutubeHandler.get_audio(url)
        return None

    @staticmethod
    def _music_from_query(query: str) -> Optional[str]:
        """Get youtube audio url based on search query.

        Perform a youtube query to obtain the related with the most views.

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
            with requests.get(
                f"https://www.youtube.com/results?search_query={query}",
                timeout=settings.player.url_fetch.timeout,
            ) as response:
                video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        return url
