import multiprocessing
import queue
from typing import Any, Iterable, Optional

from pipo.config import settings
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.music_queue import MusicQueue


class LocalMusicQueue(MusicQueue):
    """Thread safe local music queue.

    Local thread safe FIFO music queue.

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
        for _ in range(settings.player.queue.local.get_music.retries):
            try:
                return self._audio_queue.get(
                    block=settings.player.queue.local.get_music.block,
                    timeout=settings.player.queue.local.get_music.timeout,
                )
            except queue.Empty:  # noqa: PERF203
                if self.size():
                    self._logger.warning("Next music taking too long to process")
                else:
                    self._logger.info("Music queue is empty")
                    break
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

    def fetch_queue_size(self) -> int:
        """Fetch queue size."""
        return 0 if not self._audio_fetch_queue else self._audio_fetch_queue.qsize()

    def audio_queue_size(self) -> int:
        """Audio queue queue size."""
        return 0 if not self._audio_queue else self._audio_queue.qsize()
