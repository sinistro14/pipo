import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Union

class PlayerQueue(ABC):
    """Player queue.

    Handles added music progress tracking.
    """

    _logger: logging.Logger

    def __init__(
        self,
    ) -> None:
        self._logger = logging.getLogger(__name__)

    @abstractmethod
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
        pass

    @abstractmethod
    def get(self) -> Optional[str]:
        """Get one music from queue."""
        # FIXME obtain music
        music = None
        self._logger.debug("Item obtained from music queue: %s", music)
        return music

    @abstractmethod
    def get_all(self) -> Any:
        """Get all musics from queue."""
        pass

    @abstractmethod
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

    @abstractmethod
    def clear(self) -> None:
        """Clear queue."""
        # FIXME reset counters and try to delete queues if possible
        pass
