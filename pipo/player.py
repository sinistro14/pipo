#!usr/bin/env python3
import re
import time
import random
import urllib
import logging
import threading
from typing import List, Union, Optional
from multiprocessing.pool import ThreadPool

import pytube

from pipo.config import settings


class Player:

    __bot: None
    __logger: logging.Logger
    __lock: threading.Lock
    __url_fetch_pool: ThreadPool
    __player_thread: threading.Thread
    __music_queue: List[Union[str, List[str]]]
    can_play: threading.Event

    def __init__(self, bot) -> None:
        self.__player_thread = None
        self.__logger = logging.getLogger(__name__)
        self.__bot = bot
        self.__music_queue = []
        self.__lock = threading.Lock()
        self.can_play = threading.Event()
        self.__url_fetch_pool = ThreadPool(
            processes=settings.player.url_fetch.pool_size
        )

    def stop(self) -> None:
        self.__clear_queue()
        self.can_play.set()  # loop in __play_music_queue breaks due to empty queue
        self.__player_thread.join()
        self.__bot._voice_client.stop()

    def pause(self) -> None:
        self.__bot._voice_client.pause()

    def resume(self) -> None:
        self.__bot._voice_client.resume()

    async def leave(self) -> None:
        await self.__bot._voice_client.disconnect()

    def queue_size(self) -> int:
        # used for solving method reliability issues without locks
        if self.__music_queue:
            sizes = [
                len(self.__music_queue)
                for _ in range(settings.player.queue.size_check_iterations)
            ]
            return round(sum(sizes) / len(sizes))
        return 0

    def shuffle(self) -> None:
        with self.__lock:
            [random.shuffle(music) for music in self.__music_queue]
            random.shuffle(self.__music_queue)

    def skip_list(self) -> List[str]:
        with self.__lock:
            if self.queue_size() and isinstance(self.__music_queue[0], list):
                return self.__music_queue.pop()

    def play(self, queries: Union[str, List[str]], shuffle: bool = False) -> None:
        if self.__player_thread:
            if not self.__player_thread.is_alive:
                self.__player_thread.join()
                self.__player_thread = threading.Thread(
                    self.__play_music_queue, daemon=True
                )
                self.__player_thread.start()
                self.can_play.set()
        else:
            self.__player_thread = threading.Thread(
                target=self.__play_music_queue, daemon=True
            )
            self.__player_thread.start()
            self.can_play.set()
        self.__add_music(queries, shuffle)

    def __add_music(self, queries: Union[str, List[str]], shuffle: bool) -> List[str]:
        results = []
        playlist = isinstance(queries, str)
        if queries:
            queries = (
                queries
                if isinstance(queries, list)
                else [
                    queries,
                ]
            )
            shuffle and random.shuffle(queries)
            results = [
                result
                for result in self.__url_fetch_pool.map(
                    Player.get_youtube_audio,
                    queries,
                )
                if result
            ]
            with self.__lock:
                if playlist:
                    self.__music_queue.append(results)
                else:
                    self.__music_queue.extend(results)
        return results

    def __clear_queue(self) -> None:
        with self.__lock:
            self.__music_queue = []

    def __play_music_queue(self) -> None:
        while self.can_play.wait() and self.queue_size():
            self.can_play.clear()
            url = None
            with self.__lock:
                url, playlist = self.__music_queue.pop()
                if isinstance(playlist, list):  # got url or playlist?
                    url = playlist.pop()
                    if playlist:  # playlist not empty
                        self.__music_queue.insert(0, playlist)
            if url:
                try:
                    self.__bot.submit_music(url)
                except Exception as exc:
                    self.__logger.warning(
                        "Can not play next music. Error: %s", str(exc)
                    )
                    self.__bot.send_message("Can not play next music. Skipping...")
        self.can_play.clear()
        self.__bot.become_idle()

    @staticmethod
    def get_youtube_url_from_query(query: str) -> str:
        query = query.replace(" ", "+").encode("ascii", "ignore").decode()
        with urllib.request.urlopen(
            f"https://www.youtube.com/results?search_query={query}"
        ) as response:
            video_ids = re.findall(r"watch\?v=(\S{11})", response.read().decode())
            url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        return url

    @staticmethod
    def get_youtube_audio(query: str) -> Optional[str]:
        """Obtains a youtube audio url.

        Given a query or a youtube url obtains the best quality audio url available.
        Retries fetching said audio url in case of error, waiting a random period of
        time given a pre configured max interval.

        Parameters
        ----------
        query : str
            Youtube video url or query.

        Returns
        -------
        str
            Youtube audio url or None if no audio url was found.
        """
        if not (query.startswith("http") or query.startswith("https")):
            query = Player.get_youtube_url_from_query(query)
        logging.getLogger(__name__).info(
            "Trying to obtain youtube audio url for query: %s", query
        )
        url = None
        for attempt in range(settings.player.url_fetch.retries):
            logging.getLogger(__name__).debug(
                "Attempt %s to obtain youtube audio url for query: %s", attempt, query
            )
            try:  # required since library is really finicky
                url = pytube.YouTube(query).streams.get_audio_only().url
            except:
                logging.getLogger(__name__).warning(
                    "Unable to obtain audio url for query: %s", query
                )
            if url:
                logging.getLogger(__name__).info("Obtained audio url: %s", url)
                return url
            else:
                time.sleep(settings.player.url_fetch.wait * random.random())
        logging.getLogger(__name__).info(
            "Unable to obtain audio url for query: %s", query
        )
        return None
