#!usr/bin/env python3
import time
import pytest
from flaky import flaky

import tests.constants
from pipo.player.music_queue.local_music_queue import LocalMusicQueue


class TestLocalMusicQueue:
    @pytest.fixture(scope="function", autouse=True)
    def queue(self):
        return LocalMusicQueue()

    @flaky(max_runs=3, min_passes=1)
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
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        music = queue.get()
        assert music
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
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        music = queue.get()
        assert music
        assert queue.size() == final_queue_size

    # TODO test add shuffle

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
        time.sleep(tests.constants.TIME_TO_FETCH_MUSIC * len(musics))
        assert queue.size() == len(musics)
        queue.clear()
        assert queue.size() == 0
