import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Union


class MusicQueue(ABC):

    _logger: logging.Logger

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def add(self, music: Union[str, Iterable[str]]) -> None:
        pass

    @abstractmethod
    def get(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_all(self) -> Any:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def shuffle(self) -> None:
        pass
