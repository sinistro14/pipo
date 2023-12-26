import logging
import multiprocessing
import random
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Union

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair


class MusicQueue(ABC):

    _logger: logging.Logger
    _audio_queue: Any
    _audio_fetch_queue: Any
    __prefect_limit: int
    fetch_limit: multiprocessing.Semaphore

    # TODO define type for audio_queues
    def __init__(
        self, prefetch_limit: int, audio_fetch_queue: Any, audio_queue: Any
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self._audio_fetch_queue = audio_fetch_queue
        self._audio_queue = audio_queue
        self.__prefect_limit = prefetch_limit
        self.__start_queue()

    def __start_queue(self):
        self.__fetch_limit = multiprocessing.Semaphore(self.__prefect_limit)
        self.__audio_fetch_pool = multiprocessing.Pool(
            settings.player.url_fetch.pool_size,
            MusicQueue.fetch_music,
            (
                self.__fetch_limit,
                self._audio_fetch_queue,
                self,
            ),
        )

    @staticmethod
    def fetch_music(
        fetch_limit: multiprocessing.Semaphore,
        source_queue: multiprocessing.Queue,
        music_queue: Any,
    ):
        while True:
            fetch_limit.acquire()  # block until new music can be fetched
            source_pair = source_queue.get()
            handler = SourceFactory.get_source(source_pair.handler_type)
            music = handler.fetch(source_pair.query)
            music_queue._add(music)

    def add(
        self,
        query: Union[str, Iterable[str]],
        shuffle: bool = False,
        source_type: str = None,
    ) -> None:
        query = list(query) if not isinstance(query, list) else query
        sources = SourceOracle.get_sources(query, source_type)
        sources = self._parse(sources)
        if shuffle:
            random.shuffle(sources)
        if sources:
            self._submit_fetch(sources)

    def _parse(self, sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
        # prepare request to be submitted, depending on queue type, override if needed
        parsed_sources = []
        for source in sources:
            parsed_sources.extend(
                SourceFactory.get_source(source.handler_type).parse(source)
            )
        return parsed_sources

    @abstractmethod
    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        # send request to fetch_queue
        pass

    @abstractmethod
    def _add(self, music: str) -> None:
        pass

    def get(self) -> Optional[str]:
        self.__fetch_limit.release()
        music = self._get()
        self._logger.debug("Item obtained from music queue: '%s'", music)
        return music

    @abstractmethod
    def _get(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_all(self) -> Any:
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
        self.__audio_fetch_pool.terminate()
        self.__audio_fetch_pool.join()
        self.__start_queue()
        self._clear()

    @abstractmethod
    def _clear(self) -> None:
        pass
