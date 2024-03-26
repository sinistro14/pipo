import pytest

import pipo.player
import tests.constants


class TestSpotifySource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return pipo.player.audio_source.spotify_handler.SpotifyHandler()

    def test_empty_url(self, music_handler):
        assert not music_handler.handle("")

    @pytest.mark.parametrize(
        "url",
        [
            tests.constants.SPOTIFY_URL_NO_HTTPS,
            tests.constants.SPOTIFY_URL_1,
            tests.constants.SPOTIFY_URL_2,
            tests.constants.SPOTIFY_URL_3,
            tests.constants.SPOTIFY_PLAYLIST_1,
            tests.constants.SPOTIFY_ALBUM_1,
        ],
    )
    def test_intput(self, music_handler, url):
        assert music_handler.parse(music_handler.handle(url))
