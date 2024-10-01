import pytest

import pipo.player
import tests.constants


class TestYoutubeQuerySource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return pipo.player.audio_source.youtube_handler.YoutubeQueryHandler()

    async def test_empty_query(self, music_handler):
        music = await music_handler.url_from_query("")
        assert music == None

    @pytest.mark.parametrize(
        "query",
        [
            tests.constants.YOUTUBE_QUERY_1,
            tests.constants.YOUTUBE_QUERY_2,
        ],
    )
    @pytest.mark.asyncio
    async def test_query(self, music_handler, query):
        music = await music_handler.url_from_query(query)
        assert music
