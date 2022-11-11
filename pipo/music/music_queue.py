import random
from typing import List

from .component import Component
from .music import Music


class MusicQueue(Component):
    """
    The Composite class represents the complex components that may have
    children. Usually, the Composite objects delegate the actual work to their
    children and then "sum-up" the result.
    """

    _children: List[Component]

    def __init__(self) -> None:
        self._children = []

    """
    A composite object can add or remove other components (both simple or
    complex) to or from its child list.
    """

    def add(self, component: Component) -> None:
        self._children.append(component)
        component.parent = self

    def pop(self) -> Music:
        if self.count():
            element = self._children.pop()
            element.parent = None
            if element.count() > 1:  # meaning we got a queue
                self._children.insert(0, element)
            return element.pop()
        return None

    def is_composite(self) -> bool:
        return True

    def clear(self) -> None:
        [child.clear() for child in self._children]
        self._children = []

    def count(self) -> int:
        return sum([child.count() for child in self._children])

    def shuffle(self) -> None:
        [child.shuffle() for child in self._children]
        random.shuffle(self._children)

    def skiplist(self) -> None:
        if self._children[0].is_composite():
            self._children.pop()
