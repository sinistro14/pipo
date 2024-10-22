import pytest

import pipo.player
import tests.constants


@pytest.mark.unit
@pytest.mark.youtube
class TestYoutubeQuerySource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return pipo.player.audio_source.youtube_handler.YoutubeQueryHandler()

    @pytest.mark.parametrize(
        "url, expected",
        [
            ("/", "/"),
            ("//", "//"),
            (" ", "%20"),
            ("ç", "%C3%A7"),
        ],
    )
    def test_url_encoding(self, music_handler, url, expected):
        assert music_handler.encode_url(url) == expected

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
