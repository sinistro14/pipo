import random
from typing import Iterable, List, Union

import uuid6
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.models.fetch import Fetch
from pipo.player.music_queue.models.music import Music
from pipo.player.music_queue.models.music_request import MusicRequest
from pipo.player.music_queue.models.prefetch import Parse, Prefetch

def _get_server_id(): # TODO generate and store UUIDs, may be useful for request order
    return "0"

broker = RabbitBroker("amqp://guest:guest@localhost:5672/") # TODO use settings

music_processing_exch = RabbitExchange(
    "music_processing",
    type=ExchangeType.TOPIC,
    durable=True,
)

processed_music_exch = RabbitExchange(
    "processed_music",
    type=ExchangeType.TOPIC,
    durable=True,
)

youtube_queue = RabbitQueue(
    "youtube",
    routing_key="provider.youtube.*",
    durable=True,
)

spotify_queue = RabbitQueue(
    "spotify", 
    routing_key="provider.spotify.*",
    durable=True,
)

server_queue = RabbitQueue(
    "server_queue",
    routing_key=f"server_{_get_server_id()}",
    durable=True,
)

@broker.publisher("parser")
async def add(
    query: Union[str, List[str]],
    shuffle: bool = False,
) -> MusicRequest:
    query = list(query) if not isinstance(query, list) else query
    return MusicRequest(
        uuid=str(uuid6.uuid7()),
        server_id=_get_server_id(),
        shuffle=shuffle,
        query=query,
    )

@broker.subscriber("parser")
@broker.publisher("pre_fetch")
async def parse( # FIXME get better name
    request: MusicRequest,
) -> None:
    sources = SourceOracle.process_queries(request.query)
    return Prefetch(
        uuid=request.uuid,
        server_id=request.server_id,
        source_pairs=sources,
    )

@broker.subscriber("pre_fetch")
async def pre_fetch(
    request: Prefetch,
) -> None:
    sources = _pre_fetch(request.source_pairs)
    if request.shuffle:
        random.shuffle(sources)
    for source in sources:
        provider = f"provider.{source.handler_type}.{source.operation}"
        fetch = Fetch(
                uuid=request.uuid,
                server_id=request.server_id,
                provider=provider,
                operation=source.operation,
                query=source.query,
            )
        await broker.publish(
            fetch,
            routing_key=provider,
            exchange=music_processing_exch,
        )


def _pre_fetch(sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
    """Parse source pairs.

    Prepare request to be submitted, depending on queue type. Override if needed.

    Parameters
    ----------
    sources : Iterable[SourcePair]
        _description_

    Returns
    -------
    Iterable[SourcePair]
        _description_
    """
    parsed_sources = []
    for source in sources:
        parsed_sources.extend(
            SourceFactory.get_source(source.handler_type).parse(source)
        )
    return parsed_sources

@broker.subscriber(youtube_queue, music_processing_exch)
async def fetch_youtube(
    request: Fetch,
) -> None:
    pass

@broker.subscriber(spotify_queue, music_processing_exch)
async def fetch_spotify(
    request: Fetch,
) -> None:
    source = get_source() # TODO implement
    if source:
        music = Music(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=request.provider,
            operation=request.operation,
            source=source,
        )
        await broker.publish(
            music,
            routing_key=music.server_id,
            exchange=processed_music_exch,
        )
