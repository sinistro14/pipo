import random
import threading
from typing import Any, Iterable, List, Optional, Union

from pipo.config import settings
from pipo.player.music_queue.music_queue import MusicQueue


class LocalMusicQueue(MusicQueue):

    __lock: threading.Lock
    __music_queue: List[str]

    def __init__(self) -> None:
        super().__init__()
        self.__lock = threading.Lock()
        self.__music_queue = []

    def add(self, music: Union[str, Iterable[str]]) -> None:
        music = (
            [
                music,
            ]
            if isinstance(music, str)
            else music
        )
        with self.__lock:
            self.__music_queue.extend(music)

    def get(self) -> Optional[str]:
        with self.__lock:
            try:
                return self.__music_queue.pop(0)
            except IndexError:
                self._logger.exception("Music queue may be empty")
        return None

    def get_all(self) -> Any:
        return self.__music_queue

    def size(self) -> int:
        # used to solve method correctness issues without locks
        if self.__music_queue:
            sizes = [
                len(self.__music_queue)
                for _ in range(settings.player.queue.local.size_check_iterations)
            ]
            return round(sum(sizes) / len(sizes))
        return 0

    def clear(self) -> None:
        with self.__lock:
            self.__music_queue = []

    def shuffle(self) -> None:
        with self.__lock:
            random.shuffle(self.__music_queue)
