import logging
import random
from typing import Iterable

from faststream import Logger
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.models import Fetch, Music, MusicRequest, Prefetch

def _get_server_id(): # TODO generate and store UUIDs, may be useful for request order
    return "0"

broker = RabbitBroker(
    url=settings.player.queue.remote.url,
    log_level=logging.getLevelName(settings.log.level)
) # TODO add other config options

parser_queue = RabbitQueue(
    "parser",
    durable=True,
)

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
    routing_key="provider." + "youtube.*",
    durable=True,
)

spotify_queue = RabbitQueue(
    "spotify",
    routing_key="provider." + "spotify.*",
    durable=True,
)

server_queue = RabbitQueue(
    "server_queue",
    routing_key=f"server.{_get_server_id()}",
    durable=True,
    exclusive=True,
)

server_publisher = broker.publisher(parser_queue, description="TODO") # TODO add description

prefetch_publisher = broker.publisher("pre_fetch", description="TODO")
@prefetch_publisher
@broker.subscriber(parser_queue, description="TODO")
async def on_parse( # FIXME get better name
    logger: Logger,
    request: MusicRequest,
) -> Prefetch:
    sources = SourceOracle.process_queries(request.query)
    logger.debug("Processed sources: %s", sources)
    return Prefetch(
        uuid=request.uuid,
        shuffle=request.shuffle,
        server_id=request.server_id,
        source_pairs=sources,
    )

@broker.subscriber("pre_fetch", description="TODO")
async def pre_fetch(
    logger: Logger,
    request: Prefetch,
) -> None:
    sources = _pre_fetch(request.source_pairs)
    if request.shuffle:
        random.shuffle(sources)
    for source in sources:
        logger.debug("Processing source: %s", source)
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

@broker.subscriber(youtube_queue, music_processing_exch, description="TODO")
async def fetch_youtube(
    request: Fetch,
) -> None:
    source = "" # get_source() TODO implement
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
            routing_key="server." + music.server_id,
            exchange=processed_music_exch,
        )

@broker.subscriber(spotify_queue, music_processing_exch, description="TODO")
async def fetch_spotify(
    request: Fetch,
) -> None:
    source = "" # get_source() TODO implement
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
            routing_key="server." + music.server_id,
            exchange=processed_music_exch,
        )
