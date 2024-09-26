import pytest
from faststream.rabbit import TestRabbitBroker

from pipo.player.music_queue.models.provider import ProviderOperation
import tests.constants
from tests.conftest import Helpers

from pipo.config import settings
from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue._remote_music_queue import broker, dispatch, transmute_youtube, transmute_youtube_query, transmute_spotify

@pytest.mark.wip
@pytest.mark.remote_queue
class TestDispatch:

    @pytest.mark.asyncio
    async def test_dispatch_youtube(self):
        uuid = Helpers.generate_uuid()
        server_id = "0"
        query = tests.constants.YOUTUBE_URL_1

        async with TestRabbitBroker(broker) as br:

            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=[query],
            )

            transmute_request = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                query=query,
                provider="provider.youtube.default",
                operation="default",
            )

            await br.publish(dispatch_request, queue=settings.player.queue.service.dispatcher.queue)
            await dispatch.wait_call(timeout=1)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_youtube.wait_call(timeout=5)
            transmute_youtube.mock.assert_called_once_with(dict(transmute_request))
    
    @pytest.mark.asyncio
    async def test_dispatch_youtube_query(self):
        uuid = Helpers.generate_uuid()
        server_id = "0"
        query = tests.constants.YOUTUBE_QUERY_1

        async with TestRabbitBroker(broker) as br:

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
                operation="query",
            )

            await br.publish(dispatch_request, queue=settings.player.queue.service.dispatcher.queue)
            await dispatch.wait_call(timeout=1)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_youtube_query.wait_call(timeout=5)
            transmute_youtube_query.mock.assert_called_once_with(dict(transmute_request))

    @pytest.mark.asyncio
    async def test_dispatch_spotify(self):
        uuid = Helpers.generate_uuid()
        server_id = "0"
        query = tests.constants.SPOTIFY_URL_1

        async with TestRabbitBroker(broker) as br:

            dispatch_request = MusicRequest(
                server_id=server_id,
                uuid=uuid,
                query=[query],
            )

            transmute_request = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                query=query,
                provider="provider.spotify.default",
                operation="default",
            )

            await br.publish(dispatch_request, queue=settings.player.queue.service.dispatcher.queue)
            await dispatch.wait_call(timeout=1)
            dispatch.mock.assert_called_once_with(dict(dispatch_request))
            await transmute_spotify.wait_call(timeout=5)
            transmute_spotify.mock.assert_called_once_with(dict(transmute_request))
