import pytest

import pipo.player
import tests.constants


class TestYoutubeQuerySource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return pipo.player.audio_source.youtube_query_handler.YoutubeQueryHandler()

    def test_empty_query(self, music_handler):
        assert not music_handler.fetch("")

    @pytest.mark.parametrize(
        "query",
        [
            tests.constants.QUERY_1,
            tests.constants.QUERY_2,
        ],
    )
    def test_query(self, music_handler, query):
        assert music_handler.fetch(query)
