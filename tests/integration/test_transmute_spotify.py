import pytest
import mock
from faststream.rabbit import TestRabbitBroker
from pipo.player.audio_source.spotify_handler import SpotifyOperations
from pipo.player.audio_source.youtube_handler import YoutubeOperations
from pipo.player.music_queue.models.provider import ProviderOperation
import tests.constants
from tests.conftest import Helpers

from pipo.config import settings

from pipo.player.music_queue._remote_music_queue import (
    broker,
    transmute_spotify,
    transmute_youtube_query,
    provider_exch,
)


@pytest.mark.spotify
@pytest.mark.remote_queue
class TestDispatch:
    @pytest.mark.parametrize(
        "query, expected",
        [
            (tests.constants.SPOTIFY_URL_1, tests.constants.SPOTIFY_URL_1_SONG),
            (
                tests.constants.SPOTIFY_ALBUM_1,
                tests.constants.SPOTIFY_ALBUM_1_SAMPLE_SONG,
            ),
            (
                tests.constants.SPOTIFY_PLAYLIST_1,
                tests.constants.SPOTIFY_PLAYLIST_1_SAMPLE_SONG,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_transmute_spotify(self, query, expected):
        server_id = "0"
        uuid = Helpers.generate_uuid()

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            operation_request = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                provider="provider.spotify.url",
                operation=SpotifyOperations.URL,
                query=query,
            )

            provider_operations = [
                mock.call(
                    dict(
                        ProviderOperation(
                            uuid=uuid,
                            server_id=server_id,
                            query=expected,
                            provider="provider.youtube.query",
                            operation=YoutubeOperations.QUERY,
                        )
                    )
                )
            ]

            await br.publish(
                operation_request,
                exchange=provider_exch,
                routing_key=operation_request.provider,
            )
            await transmute_spotify.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            transmute_spotify.mock.assert_called_once_with(dict(operation_request))
            await transmute_youtube_query.wait_call(
                timeout=tests.constants.MEDIUM_TIMEOUT
            )
            transmute_youtube_query.mock.assert_has_calls(
                provider_operations, any_order=True
            )
