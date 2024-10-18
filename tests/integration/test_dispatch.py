import pytest
from faststream.rabbit import TestRabbitBroker
from unittest import mock
from pipo.player.audio_source.youtube_handler import YoutubeOperations
from pipo.player.audio_source.spotify_handler import SpotifyOperations
from pipo.player.music_queue.models.provider import ProviderOperation
import tests.constants
from tests.conftest import Helpers

from pipo.config import settings

from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue._remote_music_queue import (
    broker,
    dispatch,
    dispatcher_queue,
    transmute_youtube,
    transmute_youtube_query,
    transmute_youtube_playlist,
    transmute_spotify,
)


@pytest.mark.integration
@pytest.mark.remote_queue
class TestDispatch:
    @pytest.mark.asyncio
    async def test_dispatch_youtube_empty_url(self):
        server_id = "0"
        uuid = Helpers.generate_uuid()

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=[""],
            )

            await br.publish(dispatch_request, queue=dispatcher_queue)
            await dispatch.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            transmute_youtube.mock.assert_not_called()

    @pytest.mark.parametrize(
        "queries",
        [
            tests.constants.YOUTUBE_URL_1,
            tests.constants.YOUTUBE_URL_SIMPLE_LIST,
        ],
    )
    @pytest.mark.youtube
    @pytest.mark.asyncio
    async def test_dispatch_youtube_url(self, queries):
        server_id = "0"
        uuid = Helpers.generate_uuid()
        queries = [queries] if isinstance(queries, str) else queries

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=queries,
            )

            provider_operations = [
                mock.call(
                    dict(
                        ProviderOperation(
                            uuid=uuid,
                            server_id=server_id,
                            query=query,
                            provider="provider.youtube.url",
                            operation=YoutubeOperations.URL,
                        )
                    )
                )
                for query in queries
            ]

            await br.publish(dispatch_request, queue=dispatcher_queue)
            await dispatch.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_youtube.wait_call(timeout=tests.constants.MEDIUM_TIMEOUT)
            transmute_youtube.mock.assert_has_calls(provider_operations, any_order=True)

    @pytest.mark.parametrize(
        "queries",
        [
            tests.constants.YOUTUBE_PLAYLIST_1,
        ],
    )
    @pytest.mark.youtube
    @pytest.mark.asyncio
    async def test_dispatch_youtube_playlist(self, queries):
        server_id = "0"
        uuid = Helpers.generate_uuid()
        queries = [queries] if isinstance(queries, str) else queries

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=queries,
            )

            provider_operations = dict(
                ProviderOperation(
                    uuid=uuid,
                    server_id=server_id,
                    query=queries[0],
                    provider="provider.youtube.playlist",
                    operation=YoutubeOperations.PLAYLIST,
                )
            )

            await br.publish(dispatch_request, queue=dispatcher_queue)
            await dispatch.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_youtube_playlist.wait_call(
                timeout=tests.constants.MEDIUM_TIMEOUT
            )
            transmute_youtube_playlist.mock.assert_called_once_with(
                provider_operations,
            )

    @pytest.mark.query
    @pytest.mark.asyncio
    async def test_dispatch_youtube_query(self):
        uuid = Helpers.generate_uuid()
        server_id = "0"
        query = tests.constants.YOUTUBE_QUERY_1

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=[query],
            )

            transmute_request = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                query=query,
                provider="provider.youtube.query",
                operation=YoutubeOperations.QUERY,
            )

            await br.publish(dispatch_request, queue=dispatcher_queue)
            await dispatch.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_youtube_query.wait_call(
                timeout=tests.constants.MEDIUM_TIMEOUT
            )
            transmute_youtube_query.mock.assert_called_once_with(
                dict(transmute_request)
            )

    @pytest.mark.parametrize(
        "queries",
        [
            tests.constants.SPOTIFY_URL_1,
            tests.constants.SPOTIFY_ALBUM_1,
            tests.constants.SPOTIFY_PLAYLIST_1,
        ],
    )
    @pytest.mark.spotify
    @pytest.mark.asyncio
    async def test_dispatch_spotify(self, queries):
        server_id = "0"
        uuid = Helpers.generate_uuid()
        queries = [queries] if isinstance(queries, str) else queries

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=queries,
            )

            provider_operations = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                query=queries[0],
                provider="provider.spotify.url",
                operation=SpotifyOperations.URL,
            )

            await br.publish(dispatch_request, queue=dispatcher_queue)
            await dispatch.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_spotify.wait_call(timeout=tests.constants.LONG_TIMEOUT)
            transmute_spotify.mock.assert_called_once_with(dict(provider_operations))
