import pytest

import pipo.player
import tests.constants


class TestYoutubeSource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return pipo.player.audio_source.youtube_handler.YoutubeHandler()

    def test_empty_url(self, music_handler):
        assert not music_handler.fetch("")

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
    def test_url(self, music_handler, url):
        assert music_handler.fetch(url)
