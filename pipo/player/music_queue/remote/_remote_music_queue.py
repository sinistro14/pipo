import ssl
import logging
import random
from typing import Iterable

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from faststream import Context, Logger
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware
from faststream.security import BaseSecurity

from pipo.config import settings
from pipo.player.audio_source.source_factory import SourceFactory
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.audio_source.source_type import SourceType
from pipo.player.audio_source.spotify_handler import SpotifyHandler
from pipo.player.audio_source.youtube_handler import YoutubeHandler
from pipo.player.audio_source.youtube_query_handler import YoutubeQueryHandler
from pipo.player.music_queue.models import ProviderOperation, Music, MusicRequest

tracer_provider = TracerProvider(resource=Resource.create(attributes={"service.name": "faststream"}))
trace.set_tracer_provider(tracer_provider)

broker = RabbitBroker(
    app_id=settings.app,
    url=settings.player.queue.remote.url,
    host=settings.player.queue.remote.host,
    virtualhost=settings.player.queue.remote.vhost,
    port=settings.player.queue.remote.port,
    timeout=settings.player.queue.remote.timeout.broker,
    max_consumers=settings.player.queue.remote.max_consumers,
    graceful_timeout=settings.player.queue.remote.timeout.broker_graceful,
    logger=logging.getLogger(__name__),
    security=BaseSecurity(ssl_context=ssl.create_default_context()),
    middlewares=(RabbitTelemetryMiddleware(tracer_provider=tracer_provider),),
)  # TODO add other config options

dispatcher_queue = RabbitQueue(
    settings.player.queue.remote.queues.dispatcher.queue,
    durable=True,
    arguments=settings.player.queue.remote.queues.dispatcher.args,
)

server_publisher = broker.publisher(
    dispatcher_queue,
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
    arguments=settings.player.queue.remote.queues.transmuter.youtube_query.args,
)

youtube_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.youtube.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.youtube.routing_key,
    durable=True,
    arguments=settings.player.queue.remote.queues.transmuter.youtube.args,
)

spotify_queue = RabbitQueue(
    settings.player.queue.remote.queues.transmuter.spotify.queue,
    routing_key=settings.player.queue.remote.queues.transmuter.spotify.routing_key,
    durable=True,
    arguments=settings.player.queue.remote.queues.transmuter.spotify.args,
)

hub_queue = RabbitQueue(
    settings.player.queue.remote.queues.hub.queue,
    routing_key=settings.player.queue.remote.queues.hub.routing_key,
    durable=True,
    exclusive=True,
    arguments=settings.player.queue.remote.queues.hub.args,
)

hub_exch = RabbitExchange(
    settings.player.queue.remote.queues.hub.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)


@broker.subscriber(
    queue=dispatcher_queue,
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
        logger.debug("Published to provider %s request: %s", provider, request)


def __dispatch(sources: Iterable[SourcePair]) -> Iterable[SourcePair]:
    """Parse source pairs.

    Prepare request to be submitted, depending on queue type.

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
    for source in sources:  # TODO simplify logic during micro service creation
        handler = source.handler_type
        if source.operation == "query":
            handler = SourceType.YOUTUBE_QUERY
        parsed_sources.extend(SourceFactory.get_source(handler).parse(source))
    return parsed_sources


@broker.subscriber(
    queue=youtube_query_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.youtube.query key",
)
@broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.remote.queues.transmuter.youtube.routing_key,
    description="Produces to provider topic with provider.youtube.default key with increased priority",
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
            operation="default",
            query=source,
        )
        logger.debug("Resolved youtube query operation: %s", request)
        return request


@broker.subscriber(
    queue=youtube_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.youtube.default key and produces to hub exchange",
)
async def transmute_youtube(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    logger.debug("Received request: %s", request.query)
    source = YoutubeHandler.get_audio(request.query)  # get_source() TODO implement
    logger.debug("Obtained youtube audio url: %s", source)
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
        logger.debug("Published music: %s", music)


@broker.subscriber(
    queue=spotify_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.spotify.* key and produces to providers topic with provider.youtube.query",
)
async def transmute_spotify(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    tracks = SpotifyHandler.parse(request.query)
    for track in tracks:
        music = Music(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=request.provider,
            operation=request.operation,
            source=track.query,
        )
        await broker.publish(
            music,
            routing_key=settings.player.queue.remote.queues.transmuter.youtube_query.routing_key,
            exchange=provider_exch,
            correlation_id=correlation_id,
        )
        logger.debug("Published music: %s", music)
