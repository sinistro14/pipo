#!usr/bin/env python3
"""Music Player."""
import asyncio
import logging
import multiprocessing.pool
import random
import re
import time
from functools import lru_cache
from typing import List, Optional, Union

import requests
from yt_dlp import YoutubeDL

from pipo.config import settings
from pipo.player.music_queue.music_queue import MusicQueue
from pipo.player.music_queue.music_queue_factory import MusicQueueFactory


class Player:
    """Manage music and Discord voice channel interactions.

    Acts as facilitator to manage audio information while interacting with Discord.
    Maintains a music queue to which new audio sources are asynchronously added when
    calling :meth:`~Player.play`. A thread is used to stream audio to Discord
    until the music queue is exhausted. Whether such thread is allowed to continue
    consuming the queue is specified using :attr:`~Player.can_play`.

    Attributes
    ----------
    __bot : :class:`~pipo.bot.PipoBot`
        Client Discord bot.
    __logger : logging.Logger
        Class logger.
    __audio_fetch_pool : multiprocessing.pool.ThreadPool
        Obtains source information required to play music.
    __player_thread : asyncio.Task
        Obtains and plays music from :attr:`~Player._music_queue`.
    _music_queue : :class:`~pipo.player.music_queue.music_queue.MusicQueue`
        Stores music to play.
    can_play : asyncio.Event
        Whether new music from queue can be played.
    """

    __bot: None
    __logger: logging.Logger
    __audio_fetch_pool: multiprocessing.pool.ThreadPool
    __player_thread: asyncio.Task
    _music_queue: MusicQueue
    can_play: asyncio.Event

    def __init__(self, bot) -> None:
        """Build music player.

        Parameters
        ----------
        bot : :class:`~pipo.bot.PipoBot`
            Client Discord bot.
        """
        self.__bot = bot
        self.__logger = logging.getLogger(__name__)
        self.__player_thread = None
        self.can_play = asyncio.Event()
        self._music_queue = MusicQueueFactory.get(settings.player.queue.type)
        self.__audio_fetch_pool = multiprocessing.pool.ThreadPool(
            processes=settings.player.url_fetch.pool_size
        )

    def stop(self) -> None:
        """Reset music queue and halt currently playing audio."""
        self.__clear_queue()
        self.__player_thread.cancel()
        self.__bot.voice_client.stop()
        self.can_play.set()

    def skip(self) -> None:
        """Skip currently playing music."""
        self.__bot.voice_client.stop()

    def pause(self) -> None:
        """Pause currently playing music."""
        self.__bot.voice_client.pause()

    def resume(self) -> None:
        """Resume previously paused music."""
        self.__bot.voice_client.resume()

    async def leave(self) -> None:
        """Make bot leave the current server."""
        await self.__bot.voice_client.disconnect()

    def queue_size(self) -> int:
        """Get music queue size."""
        return self._music_queue.size()

    def play(self, queries: Union[str, List[str]], shuffle: bool = False) -> None:
        """Add music to play.

        Enqueues music to be played when player thread is free and broadcasts such
        availability. Music thread is initialized if not yet available.

        Parameters
        ----------
        queries : Union[str, List[str]]
            Single/list of music or playlist urls. If a query string is provided
            the best guess music is played.
        shuffle : bool, optional
            Randomize play order when multiple musics are provided, by default False.
        """
        if (not self.__player_thread) or (
            self.__player_thread
            and (self.__player_thread.done() or self.__player_thread.cancelled())
        ):
            self._start_music_queue()
        if not isinstance(queries, (list, tuple)):  # ensure an Iterable is used
            queries = [
                queries,
            ]
        self.__add_music(queries, shuffle)

    def __add_music(self, queries: List[str], shuffle: bool) -> None:
        """Add music to play queue.

        Enqueues music to be played when player thread is free and broadcasts such
        availability. Music thread is initialized if not yet available.

        Parameters
        ----------
        queries : List[str]
            List comprised of music, search query or playlist urls. If a query string is
            found the best guess music is played.
        shuffle : bool
            Randomize order by which queries are added to play queue.
        """
        self.__logger.info("Processing music query %s", queries)
        for query in queries:
            if "list=" in query:  # check if playlist
                with YoutubeDL({"extract_flat": True}) as ydl:
                    playlist_id = ydl.extract_info(url=query, download=False).get("id")
                    playlist_url = (
                        f"https://www.youtube.com/playlist?list={playlist_id}"
                    )
                    audio = [
                        url.get("url")
                        for url in ydl.extract_info(
                            url=playlist_url, download=False
                        ).get("entries")
                    ]
            else:
                audio = [  # noqa
                    query,
                ]
            if shuffle:
                random.shuffle(audio)

            self.__logger.debug("Obtaining audio %s", audio)
            for result in self.__audio_fetch_pool.imap(
                Player.get_youtube_audio,
                audio,
            ):
                self.__logger.debug("Trying to add music %s", result)
                if result:
                    self.__logger.info("Added music %s", result)
                    self._music_queue.add(result)

    def _start_music_queue(self) -> None:
        """Initialize music thread.

        Initializes music thread and allows music queue consumption.
        """
        self.can_play.set()
        self.__player_thread = asyncio.create_task(self.__play_music_queue())

    def __clear_queue(self) -> None:
        """Clear music queue."""
        self._music_queue.clear()

    async def __play_music_queue(self) -> None:
        """Play music task.

        Obtains a music from :attr:`~pipo.play.player.Player._music_queue` and creates
        a task to submit to the Discord bot to be played.
        """
        self.__logger.info("Entering music play loop")
        while await self.can_play.wait():
            if not self.queue_size():
                break
            self.can_play.clear()
            self.__logger.debug("Entered music play loop %s", self.queue_size())
            url = self._music_queue.get()
            if url:
                try:
                    await self.__bot.submit_music(url)
                except asyncio.CancelledError:
                    self.__logger.info("Play music task cancelled", exc_info=True)
                except Exception:
                    self.__logger.warning("Unable to play next music", exc_info=True)
                    await self.__bot.send_message(settings.player.messages.play_error)
            else:
                self.__logger.info(
                    "Unable to play next music, obtained invalid url %s", url
                )
                await self.__bot.send_message(settings.player.messages.play_error)
        self.can_play.set()
        self.__logger.info("Exiting play music queue loop")
        self.__bot.become_idle()

    @staticmethod
    def get_youtube_url_from_query(query: str) -> Optional[str]:
        """Get youtube video url based on search query.

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

    @staticmethod
    @lru_cache(maxsize=settings.player.url_fetch.max_cache_size)
    def get_youtube_audio(query: str) -> Optional[str]:
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
        if not query.startswith(("http", "https")):
            query = Player.get_youtube_url_from_query(query)
        logging.getLogger(__name__).debug(
            "Trying to obtain youtube audio url %s", query
        )
        url = None
        if query:
            for attempt in range(settings.player.url_fetch.retries):
                logging.getLogger(__name__).debug(
                    "Attempting %s to obtain youtube audio url %s", attempt, query
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
                    logging.getLogger(__name__).info("Obtained audio url %s", url)
                    return url
                time.sleep(settings.player.url_fetch.wait)
        logging.getLogger(__name__).warning("Unable to obtain audio url %s", query)
        return None
