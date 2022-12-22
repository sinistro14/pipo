import logging
import random
import re
import threading
import urllib
from multiprocessing.pool import ThreadPool
from typing import List, Union

from pytube import YouTube

from pipo.groovy import Groovy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Player:

    __bot: Groovy
    __lock: threading.Lock
    __url_fetch_pool: ThreadPool
    __player_thread: threading.Thread
    __music_queue: List[Union[str, List[str]]]
    can_play: threading.Event

    def __init__(self, bot: Groovy) -> None:
        self.__bot = bot
        self.__lock = threading.Lock()
        self.can_play = threading.Event()
        self.__music_queue = []
        self.__url_fetch_pool = ThreadPool(max_workers=4)  # TODO configure value

    def stop(self) -> None:
        self.__clear_queue()
        self.can_play.set()
        self.__player_thread.join()  # TODO check if join here makes sense
        self.__bot._voice_client.stop()
        self.can_play.clear()

    def pause(self) -> None:
        self.__bot._voice_client.pause()

    def resume(self) -> None:
        self.__bot._voice_client.resume()

    async def leave(self) -> None:
        await self.__bot._voice_client.disconnect()

    def queue_size(self) -> int:
        # used for solving method reliability issues without locks
        if self.__music_queue:
            sizes = [len(self.__music_queue) for _ in range(5)] # TODO configure iterations
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
                    self._play_next_music, args=(self,), daemon=True
                )
                self.__player_thread.start()
                self.can_play.set()
        else:
            self.__player_thread = threading.Thread(
                self._play_next_music, args=(self,), daemon=True
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
                    Player.get_youtube_audio_url, (queries,)
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

    def _play_next_music(self) -> None:
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
                    logger.warning("Can not play next music. Error: %s", str(exc))
                    self.__bot.send_message("Can not play next music. Skipping...")
        self.__bot.become_idle()

    @staticmethod
    def get_youtube_audio_url(query: str) -> str:
        if not query.startswith("http"):
            query = query.replace(" ", "+").encode("ascii", "ignore").decode()
            with urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={query}"
            ) as response:
                video_ids = re.findall(r"watch\?v=(\S{11})", response.read().decode())
                query = f"https://www.youtube.com/watch?v={video_ids[0]}"
        return YouTube(query).streams.get_audio_only().url
