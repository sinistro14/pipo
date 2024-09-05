import asyncio
from typing import Dict, Iterable, Optional

import uuid6
import faststream.rabbit
from expiringdict import ExpiringDict
from faststream.rabbit import RabbitRoute, RabbitRouter

from pipo.config import settings
from pipo.player.queue import PlayerQueue
from pipo.player.music_queue.models.music import Music
from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue.remote._remote_music_queue import (
    hub_exch,
    server_publisher,
    _declare_hub_queue,
)


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
    __requests: Dict[str, MusicRequest]

    def __init__(self, server_id: str) -> None:
        super().__init__()
        self.__requests = ExpiringDict(
            max_len=settings.player.queue.remote.requests.max,
            max_age_seconds=settings.player.queue.remote.requests.timeout,
        )
        self.__server_id = server_id
        self.__publisher = server_publisher
        self.__get_music = asyncio.Lock()
        # TODO consider relying only on queue max size instead of lock
        self.__playable_music = asyncio.Queue(1)  # pass to configs
        self.__start()

    def __start(self) -> None:
        RabbitRouter(
            handlers=(
                RabbitRoute(
                    self._consume_music,
                    queue=_declare_hub_queue(self.__server_id),
                    exchange=hub_exch,
                    description="Consumes from hub exchange bound exclusive hub client queue",
                ),
            )
        )

    def __generate_uuid(self) -> str:
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

    async def get(self) -> Optional[str]:
        self.__get_music.release()
        music = await self.__playable_music.get()  # TODO handle timeout
        self._logger.debug("Item obtained from music queue: %s", music)
        return music

    # queue consumer, see __start
    async def _consume_music(self, request: Music) -> None:
        await self.__get_music.acquire()
        if request.uuid in self.__requests:
            music = request.source
            self._logger.debug("Item obtained from music queue: %s", music)
            self.__playable_music.put(music)
        else:
            self._logger.warning("Item obtained was discarded: %s", music)

    def size(self) -> int:
        return self.__playable_music.qsize() + len(self.__requests)

    def clear(self) -> None:
        self.__requests.clear()
        try:
            while not self.__playable_music.empty():
                self.__playable_music.get_nowait()
        except asyncio.QueueEmpty:
            self._logger.warning("There was an error cleaning locally stored music.")
        self._logger.info("Locally stored music cleaned.")
