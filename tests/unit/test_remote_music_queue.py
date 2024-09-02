from typing import List
import pytest
from faststream.rabbit import TestRabbitBroker
from pydantic import BaseModel

import tests.constants
from tests.conftest import Helpers

from pipo.player.music_queue.remote.music_queue import RemoteMusicQueue
from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue.remote._remote_music_queue import broker, server_publisher

@pytest.mark.remote_queue
class TestFaststream:
    @pytest.mark.asyncio
    async def test_queue_add(self):

        request = MusicRequest(
            server_id="0",
            uuid=Helpers.generate_uuid(),
            query=[tests.constants.YOUTUBE_URL_1]
        )

        async with TestRabbitBroker(broker):
            await server_publisher.publish(request, server_publisher.queue.name)
            server_publisher.mock.assert_called_once_with(dict(request))

@pytest.mark.remote_queue
class TestRemoteMusicQueue:

    @pytest.mark.parametrize(
        "query, shuffle",
        [
            (tests.constants.YOUTUBE_URL_SINGLE_ELEMENT_LIST, False),
            (tests.constants.YOUTUBE_URL_SIMPLE_LIST, True),
        ],
    )
    @pytest.mark.asyncio
    async def test_music_request_send(self, query, shuffle):
        server_id = "0"
        queue = RemoteMusicQueue(server_id)

        expected = MusicRequest(
            uuid=Helpers.generate_uuid(),
            server_id=server_id,
            shuffle=shuffle,
            query=query
        )

        async with TestRabbitBroker(broker):
            await queue.add(query=query, shuffle=shuffle)
            server_publisher.mock.assert_called_once
            actual = MusicRequest(**server_publisher.mock.call_args.args[0])
            assert actual
            assert Helpers.equal_models(expected, actual, ["uuid"])
            
