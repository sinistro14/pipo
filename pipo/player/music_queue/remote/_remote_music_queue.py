import logging
import random
from typing import Iterable

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from faststream import Logger
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.spotify_handler import SpotifyHandler
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.music_queue.models import ProviderOperation, Music, MusicRequest

resource = Resource.create(attributes={"service.name": "faststream"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

broker = RabbitBroker(
    url=settings.player.queue.remote.url,
    log_level=logging.getLevelName(settings.log.level),
    middlewares=(RabbitTelemetryMiddleware(tracer_provider=tracer_provider),),
)  # TODO add other config options

dispatch_queue = RabbitQueue(
    settings.player.queue.remote.queues.dispatcher.queue,
    durable=True,
)

server_publisher = broker.publisher(
    dispatch_queue,
    description="Produces to dispatch queue",
)

provider_exch = RabbitExchange(
    settings.player.queue.remote.queues.hub.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)

youtube_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.youtube.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.routing_key
    + settings.player.queue.remote.queues.transmuter.youtube.routing_key,
    durable=True,
)

spotify_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.spotify.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.routing_key
    + settings.player.queue.remote.queues.transmuter.spotify.routing_key,
    durable=True,
)

hub_exch = RabbitExchange(
    settings.player.queue.remote.queues.hub.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)


def _declare_hub_queue(server_id: str) -> RabbitQueue:
    return RabbitQueue(
        f"server-queue-{server_id}",
        routing_key=f"server_queue.{server_id}",
        durable=True,
        exclusive=True,
    )


@broker.subscriber(
    dispatch_queue,
    description="Consumes from dispatch topic and produces to provider exchange",
)
async def dispatch(
    logger: Logger,
    request: MusicRequest,
) -> None:
    sources = SourceOracle.process_queries(request.query)
    logger.debug("Processed sources: %s", sources)
    sources = __dispatch(sources)
    if request.shuffle:
        random.shuffle(sources)
    for source in sources:
        logger.debug("Processing source: %s", source)
        provider = f"provider.{source.handler_type}.{source.operation}"
        request = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=provider,
            operation=source.operation,
            query=source.query,
        )
        await broker.publish(
            request,
            routing_key=provider,
            exchange=provider_exch,
        )


def __dispatch(sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
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


@broker.subscriber(
    youtube_queue,
    provider_exch,
    description="Consumes from providers topic with youtube.* key and produces to hub exchange",
)
async def transmute_youtube(
    request: ProviderOperation,
) -> None:
    source = YoutubeHandler.get_audio(request.query)  # get_source() TODO implement
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
            exchange=hub_exch,
        )


@broker.subscriber(
    spotify_queue,
    provider_exch,
    description="Consumes from providers topic with spotify.* key and produces to hub exchange",
)
async def transmute_spotify(
    request: ProviderOperation,
) -> None:
    source = SpotifyHandler.get_audio(request.query)
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
            exchange=hub_exch,
        )
