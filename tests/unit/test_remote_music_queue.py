import pytest
from faststream.rabbit import TestRabbitBroker

import tests.constants
from tests.conftest import Helpers

from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue.new_music_queue import broker, parser_publisher

@pytest.mark.remote_queue
class TestRemoteMusicQueue:

    @pytest.mark.asyncio
    async def test_music_request(self):

        uuid = Helpers.generate_uuid()
        request = MusicRequest(uuid=uuid, server_id="0", query=[tests.constants.YOUTUBE_URL_1])

        async with TestRabbitBroker(broker):
            await parser_publisher.publish(request, parser_publisher.queue.name)
            parser_publisher.mock.assert_called_once_with(dict(request))
