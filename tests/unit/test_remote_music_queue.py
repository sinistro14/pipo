import pytest
from faststream.rabbit import TestRabbitBroker

from pipo.player.music_queue.new_music_queue import broker, add

class TestRemoteMusicQueue:

    @pytest.mark.asyncio
    async def test_correct():
        async with TestRabbitBroker(broker) as br:
            await add(["test1"])
