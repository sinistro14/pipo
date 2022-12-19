import random
from threading import Lock
from typing import List

from pipo.music.component import Component
from pipo.music.music import Music


class MusicQueue(Component):
    _mutex: Lock
    _children: List[Component]

    def __init__(self, children: List[Component] = None) -> None:
        self._children = children or []
        self._mutex = Lock()

    def add(self, component: Component) -> None:
        with self._mutex:
            self._children.append(component)
        component.parent = self

    def pop(self) -> Music:
        """_summary_

        _extended_summary_
        Not thread safe if this method is called concurrently.

        Returns
        -------
        Music
            _description_
        """
        music = None
        if self.count():
            element = self._children.pop()
            if element.count() > 1:  # meaning we got a queue
                self._children.insert(0, element)
                element = element.pop() # get first element from queue
            element.parent = None
            music = element.pop()
        return music

    @classmethod
    def is_composite(cls) -> bool:
        return True

    def clear(self) -> None:
        with self._mutex:
            self._children = []

    def count(self) -> int:
        with self._mutex:
            return sum([child.count() for child in self._children])

    def shuffle(self) -> None:
        with self._mutex:
            for child in self._children:
                child.shuffle()
            random.shuffle(self._children)

    def skip_list(self) -> None:
        if self._children[0].is_composite():
            self._children.pop()
