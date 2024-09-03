import asyncio
from typing import Dict, Iterable

import uuid6
import faststream.rabbit
from expiringdict import ExpiringDict

from pipo.config import settings
from pipo.player.music_queue.models.music import Music
from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue.remote._remote_music_queue import broker, server_queue, server_publisher, processed_music_exch
from pipo.player.player_queue import PlayerQueue


class RemoteMusicQueue(PlayerQueue):
    """Remote music queue.

    Attributes
    ----------
    __broker : faststream.rabbit.RabbitBroker
        Controls connection to remote queues.
    """

    __server_id: str
    __get_music: asyncio.Lock
    __playable_music: asyncio.Queue[str]
    __publisher: faststream.rabbit.RabbitPublisher
    __requests : Dict[str, MusicRequest]

    def __init__(self, server_id: str) -> None:
        self.__requests = ExpiringDict(
            max_len=settings.player.queue.remote.requests.max,
            max_age_seconds=settings.player.queue.remote.requests.timeout,
        )
        self.__server_id = server_id
        self.__publisher = server_publisher
        self.__get_music = asyncio.Lock()
        # TODO consider relying only on queue max size instead of lock
        self.__playable_music = asyncio.Queue(1)

    def __generate_uuid(self):
        return str(uuid6.uuid7())

    async def add(self, query: str | Iterable[str], shuffle: bool = False) -> None:
        query = [query] if isinstance(query, str) else query
        uuid = self.__generate_uuid()
        request = MusicRequest(
                uuid=uuid,
                server_id=self.__server_id,
                shuffle=shuffle,
                query=query,
            )
        self.__requests[uuid] = request
        await self.__publisher.publish(request)

    async def get(self, request: Music) -> str | None:
        self.__get_music.release()
        music = await self.__playable_music.get() # TODO handle timeout
        RemoteMusicQueue._logger.debug("Item obtained from music queue: %s", music)
        return music

    @broker.subscriber(queue=server_queue, exchange=processed_music_exch, description="Consumes processed music.")
    async def _consume_music(self, request: Music) -> None:
        await RemoteMusicQueue.__get_music.acquire()
        if request.uuid in self.__requests:
            self.__requests.pop(request.uuid)
            music = request.source
            RemoteMusicQueue._logger.debug("Item obtained from music queue: %s", music)
            RemoteMusicQueue.__playable_music.put(music)
        else:
            RemoteMusicQueue._logger.warning("Item obtained was discarded: %s", music)

    def size(self) -> int:
        return len(self.__requests) + self.__playable_music.qsize()

    def clear(self) -> None:
        self.__playable_music.maxsize
        self.__requests.clear()
        try:
            while not self.__playable_music.empty():
                self.__playable_music.get_nowait()
        except asyncio.QueueEmpty:
            self._logger.warning("There was an error cleaning locally stored music.")
        self._logger.info("Locally stored music cleaned.")
