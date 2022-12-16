import typing
from abc import ABC, abstractmethod

Self = typing.TypeVar("Self", bound="Component")


class Component(ABC):
    @property
    def parent(self) -> Self:
        return self._parent

    @parent.setter
    def parent(self, parent: Self):
        self._parent = parent

    def add(self, component: Self) -> None:
        pass

    def pop(self) -> Self:
        pass

    @classmethod
    def is_composite(cls) -> bool:
        return False

    @abstractmethod
    def clear(self) -> None:
        self.parent = None

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def shuffle(self) -> None:
        pass

    @abstractmethod
    def skip_list(self) -> None:
        pass
