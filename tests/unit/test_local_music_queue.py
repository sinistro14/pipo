#!usr/bin/env python3
import time
import pytest
from flaky import flaky

import tests.constants
from pipo.player.music_queue.local_music_queue import LocalMusicQueue

def assert_music(music):
    assert music, f"Invalid music, received {music}"

def assert_queue_size(actual, expected):
    assert actual == expected, \
        f"Expected queue of size {expected}, received {actual}"

@flaky(max_runs=5, min_passes=1)
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
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC)
        assert_queue_size(queue.size(), queue_size)

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
        assert_queue_size(queue.size(), queue_size)

    @pytest.mark.parametrize(
        "musics, final_queue_size",
        [
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 0),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 1),
        ],
    )
    def test_get_after_individual_add(self, queue, musics, final_queue_size):
        [queue.add(music) for music in musics]
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        assert_music(queue.get())
        assert_queue_size(queue.size(), final_queue_size)

    @pytest.mark.parametrize(
        "musics, final_queue_size",
        [
            (tests.constants.MUSIC_SINGLE_ELEMENT_LIST, 0),
            (tests.constants.MUSIC_SIMPLE_LIST_1, 1),
        ],
    )
    def test_get_after_multiple_add(self, queue, musics, final_queue_size):
        queue.add(musics)
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        assert_music(queue.get())
        assert_queue_size(queue.size(), final_queue_size)

    @pytest.mark.parametrize(
        "musics",
        [
            tests.constants.MUSIC_SINGLE_ELEMENT_LIST,
            tests.constants.MUSIC_SIMPLE_LIST_2,
        ],
    )
    def test_clear(self, queue, musics):
        queue.add(musics)
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        assert_queue_size(queue.size(), len(musics))
        queue.clear()
        assert_queue_size(queue.size(), 0)
