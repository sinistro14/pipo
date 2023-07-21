#!usr/bin/env python3
import pytest

import tests.constants
from pipo.music_queue.local_music_queue import LocalMusicQueue


class TestLocalMusicQueue:
    @pytest.fixture(scope="function", autouse=True)
    def queue(self):
        return LocalMusicQueue()

    @pytest.mark.parametrize(
        "musics, queue_size",
        [
            (tests.constants.MUSIC_EMPTY_LIST, 0),
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 1),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 2),
        ],
    )
    def test_individual_add(self, queue, musics, queue_size):
        [queue.add(music) for music in musics]
        assert queue.size() == queue_size

    @pytest.mark.parametrize(
        "musics, queue_size",
        [
            (tests.constants.MUSIC_EMPTY_LIST, 0),
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 1),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 2),
        ],
    )
    def test_multiple_add(self, queue, musics, queue_size):
        queue.add(musics)
        assert queue.size() == queue_size

    @pytest.mark.parametrize(
        "musics, final_queue_size",
        [
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 0),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 1),
        ],
    )
    def test_get_after_individual_add(self, queue, musics, final_queue_size):
        [queue.add(music) for music in musics]
        music = queue.get()
        assert music == musics[0]
        assert queue.size() == final_queue_size

    @pytest.mark.parametrize(
        "musics, final_queue_size",
        [
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 0),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 1),
        ],
    )
    def test_get_after_multiple_add(self, queue, musics, final_queue_size):
        queue.add(musics)
        music = queue.get()
        assert music == musics[0]
        assert queue.size() == final_queue_size

    def test_empty_queue_shuffle(self, queue):
        queue.shuffle()
        assert queue.size() == 0

    def test_single_music_shuffle(self, helpers, queue):
        queue.add("a")
        old_queue = queue.get_all().copy()
        queue.shuffle()
        assert queue.size() == 1
        assert helpers.equal_iterables(old_queue, queue.get_all())

    @pytest.mark.parametrize(
        "musics",
        [
            tests.constants.MUSIC_SIMPLE_LIST_3,
            tests.constants.MUSIC_COMPLEX_LIST_1,
        ],
    )
    def test_multiple_music_shuffle(self, helpers, queue, musics):
        queue.add(musics)
        old_queue = queue.get_all().copy()
        queue.shuffle()
        assert queue.size() == len(musics)
        assert not helpers.equal_iterables(old_queue, queue.get_all())

    @pytest.mark.parametrize(
        "musics",
        [
            tests.constants.MUSIC_SINGLE_ELEMENT_LIST,
            tests.constants.MUSIC_SIMPLE_LIST_2,
            tests.constants.MUSIC_COMPLEX_LIST_1,
        ],
    )
    def test_clear(self, queue, musics):
        queue.add(musics)
        assert queue.size() == len(musics)
        queue.clear()
        assert queue.size() == 0
