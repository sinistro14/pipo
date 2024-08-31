import logging
import multiprocessing
import random
from abc import abstractmethod
from typing import Any, Iterable, Optional, Union

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.player_queue import PlayerQueue


class MusicQueue(PlayerQueue):
    """Music queue.

    Handles added music prefetch and storage.
    Prefetch operations are transparently scheduled by the music queue but such method's
    are implemented by _submit_fetch and _add.
    Music queries are initially sent to prefetch queue from where initial information
    will be extracted. Afterwards music is obtained up to defined __prefetch_limit value
    until a music is extract from the queue.
    """

    _logger: logging.Logger
    _audio_queue: Any
    _audio_fetch_queue: Any
    __prefect_limit: int
    __fetch_pool_enabled: multiprocessing.Event
    __fetch_limit: multiprocessing.Semaphore

    def __init__(
        self, prefetch_limit: int, audio_fetch_queue: Any, audio_queue: Any
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self._audio_fetch_queue = audio_fetch_queue
        self._audio_queue = audio_queue
        self.__prefect_limit = prefetch_limit
        self.__start_queue()

    def __start_queue(self):
        """Initialize music queue."""
        self.__fetch_pool_enabled = multiprocessing.Event()
        self.__fetch_pool_enabled.set()
        self.__fetch_limit = multiprocessing.Semaphore(self.__prefect_limit)
        self.__audio_fetch_pool = multiprocessing.Pool(
            settings.player.url_fetch.pool_size,
            MusicQueue.fetch_music,
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
        source_queue: multiprocessing.Queue,  # FIXME temporary type, change later
        music_queue: Any,
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
        music_queue : Any
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
        query = list(query) if not isinstance(query, list) else query
        sources = SourceOracle.process_queries(query)
        sources = self._parse(sources)
        if shuffle:
            random.shuffle(sources)
        if sources:
            self._submit_fetch(sources)

    def _parse(self, sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
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
            parsed_sources.extend(
                SourceFactory.get_source(source.handler_type).parse(source)
            )
        return parsed_sources

    @abstractmethod
    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        """Submit request to fetch queue."""
        pass

    @abstractmethod
    def _add(self, music: str) -> None:
        pass

    def get(self) -> Optional[str]:
        """Get one music from queue."""
        self.__fetch_limit.release()
        music = self._get()
        self._logger.debug("Item obtained from music queue: %s", music)
        return music

    @abstractmethod
    def _get(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_all(self) -> Any:
        """Get all musics from queue."""
        pass

    def size(self) -> int:
        """Music to be played.

        Sum of enqueued and yet to process music.
        Estimates queue size calculating the average of several samples, solving method
        correctness issues without locks.

        Returns
        -------
        int
            Queue size.
        """
        return self.fetch_queue_size() + self.audio_queue_size()

    @abstractmethod
    def fetch_queue_size(self) -> int:
        """Queue of yet to process music size.

        Returns
        -------
        int
            Queue size.
        """
        return -1

    @abstractmethod
    def audio_queue_size(self) -> int:
        """Queue of processed music size.

        Returns
        -------
        int
            Queue size.
        """
        return -1

    def clear(self) -> None:
        """Clear all queues."""
        try:
            self._logger.info("Clearing music queue")
            self._logger.debug("Temporarily disabling queues")
            self.__fetch_pool_enabled.clear()
            self._logger.debug("Clearing queues")
            self._clear()
            self._logger.debug("Resetting fetch semaphore")
            [self.__fetch_limit.release() for _ in range(self.__prefect_limit)]
            self._logger.debug("Enabling queues")
            self.__fetch_pool_enabled.set()
            self._logger.info("Clear operation concluded")
        except Exception:
            self._logger.exception("Unable to clear music queue")
            raise

    @abstractmethod
    def _clear(self) -> None:
        pass
