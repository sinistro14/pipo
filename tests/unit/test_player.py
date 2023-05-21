import pytest
import functools

import pipo.player
import tests.constants


class TestPlayer:

    @pytest.fixture(scope="function", autouse=True)
    def player(self, mocker):
        player = pipo.player.Player(None)
        # disable music queue consumption
        mocker.patch.object(player, '_start_music_queue')
        return player

    @pytest.mark.parametrize("url", tests.constants.URL_SIMPLE_LIST)
    def test_get_youtube_audio(self, player, url):
        assert player.get_youtube_audio(url)

    @pytest.mark.parametrize(
        "url",
        [
            tests.constants.URL_1,
            tests.constants.URL_2,
            tests.constants.URL_3,
            tests.constants.URL_4,
            tests.constants.URL_5,
        ],
    )
    def test_play_url(self, player, url):
        player.play(url)
        assert player.queue_size() == 1

    @pytest.mark.parametrize(
        "url_list",
        [
            [],
            tests.constants.URL_SIMPLE_LIST,
            tests.constants.URL_COMPLEX_LIST,
        ],
    )
    def test_play_url_list(self, player, url_list):
        player.play(url_list)
        assert player.queue_size() == len(url_list)

    @pytest.mark.parametrize(
        "url_list",
        [
            tests.constants.URL_SIMPLE_LIST,
            tests.constants.URL_COMPLEX_LIST,
        ],
    )
    def test_shuffle(self, player, url_list):
        music_urls = player.play(url_list)
        initial_music_queue = player._get_music_queue().copy()
        player.shuffle()
        shuffled_music_queue = player._get_music_queue().copy()
        assert not functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q, initial_music_queue, shuffled_music_queue), True)
        assert len(music_urls) >= 0
