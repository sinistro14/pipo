import logging
import random
from typing import Iterable

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from faststream import Context, Logger
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.spotify_handler import SpotifyHandler
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler
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
    settings.player.queue.remote.queues.transmuter.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)

youtube_query_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.youtube_query.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.youtube_query.routing_key,
    durable=True,
)

youtube_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.youtube.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.youtube.routing_key,
    durable=True,
)

spotify_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.spotify.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.spotify.routing_key,
    durable=True,
)

hub_queue = RabbitQueue(
    settings.player.queue.remote.queues.hub.queue,
    routing_key=settings.player.queue.remote.queues.hub.routing_key,
    durable=True,
    exclusive=True,
)

hub_exch = RabbitExchange(
    settings.player.queue.remote.queues.hub.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)


@broker.subscriber(
    queue=dispatch_queue,
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
        logger.info("Processing source: %s", source)
        provider = (
            settings.player.queue.remote.queues.transmuter.routing_key
            + source.handler_type
            + "."
            + source.operation
        )
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
        logger.info("Published to provider %s request: %s", provider, request)


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
    queue=youtube_query_queue,
    exchange=provider_exch,
    description="Consumes from providers topic with provider.youtube_query.query key and produces to hub exchange",
)
@broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.remote.queues.transmuter.routing_key
    + "youtube.query",  # FIXME decouple handler class names from queue processing
    description="TODO",
    priority=1,
)
async def transmute_youtube_query(
    request: ProviderOperation,
    logger: Logger,
) -> None:
    source = YoutubeQueryHandler._music_from_query(request.query)
    if source:
        request = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider="youtube",
            operation="query",
            query=source,
        )
        return request


@broker.subscriber(
    queue=youtube_queue,
    exchange=provider_exch,
    description="Consumes from providers topic with provider.youtube.default key and produces to hub exchange",
)
async def transmute_youtube(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    logger.info("Received request: %s", request.query)
    source = YoutubeHandler.get_audio(request.query)  # get_source() TODO implement
    logger.info("Obtained youtube audio url: %s", source)
    if source:
        music = Music(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=request.provider,
            operation=request.operation,
            source=source,
        )
        routing_key = (
            settings.player.queue.remote.queues.hub.base_routing_key + music.server_id
        )
        await broker.publish(
            music,
            routing_key=routing_key,
            exchange=hub_exch,
            correlation_id=correlation_id,
        )
        logger.info("Published to routing key %s music: %s", routing_key, music)


@broker.subscriber(
    queue=spotify_queue,
    exchange=provider_exch,
    description="Consumes from providers topic with provider.spotify.* key and produces to hub exchange",
)
async def transmute_spotify(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
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
            routing_key=settings.player.queue.remote.queues.hub.base_routing_key
            + music.server_id,
            exchange=hub_exch,
            correlation_id=correlation_id,
        )
        logger.debug("Published music: %s", music)
