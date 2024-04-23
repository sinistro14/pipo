import pytest
from flaky import flaky

import pipo.player
import tests.constants


class TestPlayer:
    @pytest.fixture(scope="function", autouse=True)
    def player(self, mocker):
        player = pipo.player.Player(None)
        # disable music queue consumption
        mocker.patch.object(player, "_start_music_queue")
        return player

    @pytest.mark.parametrize(
        "url, queue_size",
        [
            ("", 0),
            (tests.constants.YOUTUBE_URL_1, 1),
            (tests.constants.YOUTUBE_URL_2, 1),
            (tests.constants.YOUTUBE_URL_3, 1),
            (tests.constants.YOUTUBE_URL_4, 1),
            (tests.constants.YOUTUBE_URL_5, 1),
        ],
    )
    async def test_play_single_url(self, player, url, queue_size):
        player.play(url)
        assert player.queue_size() == queue_size

    @flaky(max_runs=3, min_passes=1)
    @pytest.mark.parametrize(
        "url_list",
        [
            [],
            tests.constants.YOUTUBE_URL_SIMPLE_LIST,
            tests.constants.YOUTUBE_URL_COMPLEX_LIST,
        ],
    )
    async def test_play_multiple_url(self, player, url_list):
        player.play(url_list)
        assert player.queue_size() == len(url_list)

    @flaky(max_runs=3, min_passes=1)
    @pytest.mark.parametrize(
        "playlist, playlist_size",
        [
            (tests.constants.YOUTUBE_PLAYLIST_SOURCE_1, 1),
            (tests.constants.YOUTUBE_PLAYLIST_1, 1),
            (tests.constants.YOUTUBE_PLAYLIST_SOURCE_2, 5),
            (tests.constants.YOUTUBE_PLAYLIST_2, 5),
        ],
    )
    async def test_playlist(self, player, playlist, playlist_size):
        player.play(playlist)
        assert player.queue_size() == playlist_size
