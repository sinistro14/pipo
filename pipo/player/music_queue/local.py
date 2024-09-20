import multiprocessing
import queue
import random
from typing import Any, Iterable, Optional, Self, Union

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType
from pipo.player.queue import PlayerQueue


class LocalMusicQueue(PlayerQueue):
    """Thread safe local music queue.

    Local thread safe FIFO music queue handles added music prefetch and storage.
    Prefetch operations are transparently scheduled by the music queue but such method's
    are implemented by _submit_fetch and _add.
    Music queries are initially sent to prefetch queue from where initial information
    will be extracted. Afterwards music is obtained up to defined __prefetch_limit value
    until a music is extract from the queue.
    """

    _audio_queue: multiprocessing.Queue
    _audio_fetch_queue: multiprocessing.Queue
    __prefect_limit: int
    __fetch_pool_enabled: multiprocessing.Event
    __fetch_limit: multiprocessing.Semaphore

    def __init__(self) -> None:
        super().__init__()
        audio_fetch_queue = multiprocessing.Queue()
        audio_queue = multiprocessing.Queue()
        self._audio_fetch_queue = audio_fetch_queue
        self._audio_queue = audio_queue
        self.__prefect_limit = settings.player.queue.local.prefetch_limit
        self.__start_queue()

    def __start_queue(self):
        """Initialize music queue."""
        self.__fetch_pool_enabled = multiprocessing.Event()
        self.__fetch_pool_enabled.set()
        self.__fetch_limit = multiprocessing.Semaphore(self.__prefect_limit)
        self.__audio_fetch_pool = multiprocessing.Pool(
            settings.player.url_fetch.pool_size,
            LocalMusicQueue.fetch_music,
            (
                self.__fetch_pool_enabled,
                self.__fetch_limit,
                self._audio_fetch_queue,
                self,
            ),
        )

    @staticmethod
    def fetch_music(
        worker_enabled: multiprocessing.Event,
        fetch_limit: multiprocessing.Semaphore,
        source_queue: multiprocessing.Queue,
        music_queue: Self,
    ):
        """Fetch music task.

        Task used by workers to process source data into music urls.

        Parameters
        ----------
        worker_enabled : multiprocessing.Event
            Controls whether workers are enabled.
        fetch_limit : multiprocessing.Semaphore
            Defines max music queries to process.
        source_queue : multiprocessing.Queue
            Queue from were to obtain source data.
        music_queue : LocalMusicQueue
            Queue were resultant music is added.
        """
        while True:
            if worker_enabled.wait() and fetch_limit.acquire(
                block=True, timeout=settings.player.url_fetch.lock_timeout
            ):  # block until new music can be fetched
                source_pair = source_queue.get()
                handler = SourceFactory.get_source(source_pair.handler_type)
                music = handler.fetch(source_pair.query)
                music_queue._add(music)

    def add(
        self,
        query: Union[str, Iterable[str]],
        shuffle: bool = False,
    ) -> None:
        """Add music query to queue.

        Parameters
        ----------
        query : Union[str, Iterable[str]]
            Music query to add.
        shuffle : bool, optional
            Whether to shuffle music order, by default False.
        """
        query = [query] if isinstance(query, str) else query
        sources = SourceOracle.process_queries(query)
        sources = self.__parse(sources)
        if shuffle:
            random.shuffle(sources)
        if sources:
            self._submit_fetch(sources)

    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        for source in sources:
            self._audio_fetch_queue.put_nowait(source)

    def __parse(self, sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
        """Parse source pairs.

        Prepare request to be submitted, depending on queue type. Override if needed.

        Parameters
        ----------
        sources : Iterable[SourcePair]
            _description_

        Returns
        -------
        Iterable[SourcePair]
            _description_
        """
        parsed_sources = []
        for source in sources:
            handler = source.handler_type
            if source.operation == "query":
                handler = SourceType.YOUTUBE_QUERY
            parsed_sources.extend(SourceFactory.get_source(handler).parse(source))
        return parsed_sources

    def _add(self, music: str) -> None:
        """Add item to queue."""
        self._audio_queue.put_nowait(music)

    def get(self) -> Optional[str]:
        """Get one music from queue."""
        self.__fetch_limit.release()
        music = self.__get()
        self._logger.debug("Item obtained from music queue: %s", music)
        return music

    def __get(self) -> Optional[str]:
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

    def clear(self) -> None:
        """Clear all queues."""
        try:
            self._logger.info("Clearing music queue")
            self._logger.debug("Temporarily disabling queues")
            self.__fetch_pool_enabled.clear()
            self._logger.debug("Clearing queues")
            self.__clear()
            self._logger.debug("Resetting fetch semaphore")
            [self.__fetch_limit.release() for _ in range(self.__prefect_limit)]
            self._logger.debug("Enabling queues")
            self.__fetch_pool_enabled.set()
            self._logger.info("Clear operation concluded")
        except Exception:
            self._logger.exception("Unable to clear music queue")
            raise

    def __clear(self) -> None:
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
        """Music to be played.

        Sum of enqueued and yet to process music.

        Returns
        -------
        int
            Queue size.
        """
        return self.__fetch_queue_size() + self.__audio_queue_size()

    def __fetch_queue_size(self) -> int:
        """Fetch queue size."""
        return 0 if not self._audio_fetch_queue else self._audio_fetch_queue.qsize()

    def __audio_queue_size(self) -> int:
        """Audio queue queue size."""
        return 0 if not self._audio_queue else self._audio_queue.qsize()
