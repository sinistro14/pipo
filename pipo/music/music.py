from typing import TypeVar

from pipo.music.component import Component

Self = TypeVar("Self", bound="Music")


class Music(Component):
    """
    The Leaf class represents the end objects of a composition. A leaf can't
    have any children.

    Usually, it's the Leaf objects that do the actual work, whereas Composite
    objects only delegate to their sub-components.
    """

    _query: None

    def __init__(self, query) -> None:
        super().__init__()
        self._query = query

    def count(self) -> int:
        return 1

    def pop(self) -> Component:
        return self._query

    def skip_list(self) -> None:
        pass
