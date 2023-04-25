import pytest

import pipo.player
import tests.constants


class TestPlayer:
    @pytest.mark.parametrize("url", tests.constants.URL_SIMPLE_LIST)
    def test_get_youtube_audio(self, url):
        player = pipo.player.Player(None)
        assert player.get_youtube_audio(url)

    @pytest.mark.parametrize(
        "url",
        [
            tests.constants.URL_1,
            tests.constants.URL_2,
            tests.constants.URL_3,
        ],
    )
    def test_play_url(self, url):
        player = pipo.player.Player(None)
        player.play(url)
        assert player.queue_size() == 1

    @pytest.mark.parametrize(
        "url_list",
        [
            [],
            tests.constants.URL_SIMPLE_LIST,
        ],
    )
    def test_play_url_list(self, url_list):
        player = pipo.player.Player(None)
        player.play(url_list)
        assert player.queue_size() == len(url_list)
