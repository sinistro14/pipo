from typing import TypeVar

from .component import Component

Self = TypeVar("Self", bound="Music")


class Music(Component):
    """
    The Leaf class represents the end objects of a composition. A leaf can't
    have any children.

    Usually, it's the Leaf objects that do the actual work, whereas Composite
    objects only delegate to their sub-components.
    """

    def count(self) -> int:
        return 1

    def pop(self) -> Self:
        return self

    def skiplist(self) -> None:
        pass
