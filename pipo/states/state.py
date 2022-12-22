from abc import ABC, abstractmethod

from discord.ext.commands import Context as Dctx

from pipo.states.context import Context


class State(ABC):
    """
    Declares methods that all Concrete State should
    implement and also provides a backreference to the Context object
    associated with State. This backreference can be used by States to
    transition Context to another State.
    """

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def join(self, ctx: Dctx) -> None:
        pass

    @abstractmethod
    def play(self, ctx: Dctx) -> None:
        pass

    @abstractmethod
    def play_list(self, ctx: Dctx, shuffle: bool) -> None:
        pass

    @abstractmethod
    def skip(self, skip_list: bool) -> None:
        pass

    @abstractmethod
    def leave(self) -> None:
        pass

    @abstractmethod
    def resume(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def pause(self) -> None:
        pass
