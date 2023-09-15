import multiprocessing
import queue
from typing import Any, Iterable, Optional

from pipo.config import settings
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.music_queue import MusicQueue


class LocalMusicQueue(MusicQueue):
    """Thread safe local music queue.

    Local FIFO music queue with thread safe implementation.

    Attributes
    ----------
    __lock : threading.Lock
        Controls queue altering methods.
    """

    _audio_fetch_queue: multiprocessing.Queue
    _audio_queue: multiprocessing.Queue

    def __init__(self) -> None:
        audio_fetch_queue = multiprocessing.Queue()
        audio_queue = multiprocessing.Queue()
        super().__init__(
            settings.player.queue.local.prefetch_limit,
            audio_fetch_queue,
            audio_queue,
        )

    def _add(self, music: str) -> None:
        """Add item to queue."""
        self._audio_queue.put_nowait(music)

    def _get(self) -> Optional[str]:
        """Get queue item."""
        try:
            return self._audio_queue.get_nowait() # FIXME check empty answer exception
        except queue.Empty:
            self._logger.exception("Music queue is empty")
        return None

    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        for source in sources:
            self._audio_fetch_queue.put_nowait(source)

    def _clear(self) -> None:
        """Clear queue."""
        try:
            while True:
                self._audio_fetch_queue.get_nowait()
        except queue.Empty:
            self._logger.info("Music fetch queue was cleaned.")

        try:
            while True:
                self._audio_queue.get_nowait()
        except queue.Empty:
            self._logger.info("Music queue was cleaned.")

    def get_all(self) -> Any:
        """Get enqueued music."""
        return self._audio_queue

    def size(self) -> int:
        """Queue size.

        Sum of enqueued and yet to process music.
        Estimates queue size calculating the average of several samples, solving method
        correctness issues without locks.

        Returns
        -------
        int
            Queue size.
        """
        size = 0
        if self._audio_fetch_queue:
            size += self._audio_fetch_queue.qsize()
        if self._audio_queue:
            size += self._audio_queue.qsize()
        return size
