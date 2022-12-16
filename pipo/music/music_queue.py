import random
from typing import List

from pipo.music.component import Component
from pipo.music.music import Music


class MusicQueue(Component):

    _children: List[Component]

    def __init__(self, children: List[Component] = None) -> None:
        self._children = children or []

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

    @classmethod
    def is_composite(cls) -> bool:
        return True

    def clear(self) -> None:
        for child in self._children:
            child.clear()
        self._children = []

    def count(self) -> int:
        return sum([child.count() for child in self._children])

    def shuffle(self) -> None:
        for child in self._children:
            child.shuffle()
        random.shuffle(self._children)

    def skip_list(self) -> None:
        if self._children[0].is_composite():
            self._children.pop()
