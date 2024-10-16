import ssl
import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from faststream import Context, Logger
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware
from faststream.security import BaseSecurity

from pipo.config import settings
from pipo.player.audio_source.source_oracle import SourceOracle
from pipo.player.audio_source.spotify_handler import SpotifyHandler
from pipo.player.audio_source.youtube_handler import (
    YoutubeHandler,
    YoutubeOperations,
    YoutubeQueryHandler,
)
from pipo.player.music_queue.models import ProviderOperation, Music, MusicRequest

tracer_provider = TracerProvider(
    resource=Resource.create(attributes={"service.name": "faststream"})
)
trace.set_tracer_provider(tracer_provider)

broker = RabbitBroker(
    app_id=settings.app,
    url=settings.player.queue.broker.url,
    host=settings.player.queue.broker.host,
    virtualhost=settings.player.queue.broker.vhost,
    port=settings.player.queue.broker.port,
    timeout=settings.player.queue.broker.timeout,
    max_consumers=settings.player.queue.broker.max_consumers,
    graceful_timeout=settings.player.queue.broker.graceful_timeout,
    logger=logging.getLogger(__name__),
    security=BaseSecurity(ssl_context=ssl.create_default_context()),
    middlewares=(RabbitTelemetryMiddleware(tracer_provider=tracer_provider),),
)

plq = RabbitQueue(
    name=settings.player.queue.service.parking_lot.queue,
    durable=settings.player.queue.service.parking_lot.durable,
)

dlx = RabbitExchange(
    name=settings.player.queue.service.dead_letter.exchange.name,
    type=ExchangeType.TOPIC,
    durable=settings.player.queue.service.dead_letter.exchange.durable,
)

dlq = RabbitQueue(
    name=settings.player.queue.service.dead_letter.queue.name,
    durable=settings.player.queue.service.dead_letter.queue.durable,
    routing_key=settings.player.queue.service.dead_letter.queue.routing_key,
    arguments=settings.player.queue.service.dead_letter.queue.args,
)

async def declare_dlx(b: RabbitBroker):
    await b.declare_queue(plq)
    await b.declare_exchange(dlx)
    await b.declare_queue(dlq)

dispatcher_queue = RabbitQueue(
    settings.player.queue.service.dispatcher.queue,
    durable=True,
    arguments=settings.player.queue.service.dispatcher.args,
)

server_publisher = broker.publisher(
    dispatcher_queue,
    description="Produces to dispatch queue",
)

provider_exch = RabbitExchange(
    settings.player.queue.service.transmuter.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)

youtube_playlist_queue = RabbitQueue(
    settings.player.queue.service.transmuter.youtube_playlist.queue,
    routing_key=settings.player.queue.service.transmuter.youtube_playlist.routing_key,
    durable=True,
    arguments=settings.player.queue.service.transmuter.youtube_playlist.args,
)

youtube_playlist_publisher = broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.service.transmuter.youtube.routing_key,
    description="Produces to provider exchange with key provider.youtube.url",
)

youtube_query_queue = RabbitQueue(
    settings.player.queue.service.transmuter.youtube_query.queue,
    routing_key=settings.player.queue.service.transmuter.youtube_query.routing_key,
    durable=True,
    arguments=settings.player.queue.service.transmuter.youtube_query.args,
)

youtube_queue = RabbitQueue(
    settings.player.queue.service.transmuter.youtube.queue,
    routing_key=settings.player.queue.service.transmuter.youtube.routing_key,
    durable=True,
    arguments=settings.player.queue.service.transmuter.youtube.args,
)

spotify_queue = RabbitQueue(
    settings.player.queue.service.transmuter.spotify.queue,
    routing_key=settings.player.queue.service.transmuter.spotify.routing_key,
    durable=True,
    arguments=settings.player.queue.service.transmuter.spotify.args,
)

spotify_publisher = broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.service.transmuter.youtube_query.routing_key,
    description="Produces to provider exchange with key provider.spotify.url",
)

hub_exch = RabbitExchange(
    settings.player.queue.service.hub.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)

hub_queue = RabbitQueue(
    settings.player.queue.service.hub.queue,
    routing_key=settings.player.queue.service.hub.routing_key,
    durable=settings.player.queue.service.hub.durable,
    exclusive=settings.player.queue.service.hub.exclusive,
    arguments=settings.player.queue.service.hub.args,
)


@broker.subscriber(
    queue=dispatcher_queue,
    description="Consumes from dispatch topic and produces to provider exchange",
)
async def dispatch(
    logger: Logger,
    request: MusicRequest,
) -> None:
    logger.debug("Processing request: %s", request)
    sources = SourceOracle.process_queries(request.query, request.shuffle)
    for source in sources:
        logger.debug("Processing source: %s", source)
        provider = f"{settings.player.queue.service.transmuter.routing_key}.{source.handler_type}.{source.operation}"
        request = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=provider,
            operation=source.operation,
            shuffle=request.shuffle,
            query=source.query,
        )
        logger.debug("Will publish to provider %s request: %s", provider, request)
        await broker.publish(
            request,
            routing_key=provider,
            exchange=provider_exch,
        )
        logger.info("Published request: %s", request.uuid)


@broker.subscriber(
    queue=youtube_query_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.youtube.query key",
)
@broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.service.transmuter.youtube.routing_key,
    description="Produces to provider topic with provider.youtube.url key with increased priority",
    priority=settings.player.queue.service.transmuter.youtube_query.message_priority,
)
async def transmute_youtube_query(
    request: ProviderOperation,
    logger: Logger,
) -> ProviderOperation:
    logger.debug("Received request: %s", request)
    source = await YoutubeQueryHandler.url_from_query(request.query)
    if source:
        request = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=settings.player.queue.service.transmuter.youtube.routing_key,
            operation=YoutubeOperations.URL,
            query=source,
        )
        logger.info("Transmuted youtube query: %s", request.uuid)
        return request


@broker.subscriber(
    queue=youtube_playlist_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.youtube.playlist key",
)
async def transmute_youtube_playlist(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    logger.debug("Received request: %s", request)
    tracks = YoutubeHandler.parse_playlist(request.query)
    for url in tracks:
        query = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=settings.player.queue.service.transmuter.youtube.routing_key,
            operation=YoutubeOperations.URL,
            query=url,
        )
        await youtube_playlist_publisher.publish(
            query,
            correlation_id=correlation_id,
        )
    logger.info("Transmuted youtube playlist: %s", request.uuid)


@broker.subscriber(
    queue=youtube_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.youtube.url key and produces to hub exchange",
)
async def transmute_youtube(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    logger.debug("Received request: %s", request)
    source = YoutubeHandler.get_audio(request.query)
    logger.debug("Obtained youtube audio url: %s", source)
    if source:
        music = Music(
            uuid=request.uuid,
            server_id=request.server_id,
            source=source,
        )
        routing_key = (
            f"{settings.player.queue.service.hub.base_routing_key}.{music.server_id}"
        )
        await broker.publish(
            music,
            routing_key=routing_key,
            exchange=hub_exch,
            correlation_id=correlation_id,
        )
        logger.info("Transmuted youtube music: %s", music.uuid)


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
    logger.debug("Received request: %s", request)
    tracks = await SpotifyHandler.tracks_from_query(request.query, request.shuffle)
    for track in tracks:
        query = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=settings.player.queue.service.transmuter.youtube_query.routing_key,
            operation=YoutubeOperations.QUERY,
            query=track.query,
        )
        await spotify_publisher.publish(
            query,
            correlation_id=correlation_id,
        )
    logger.info("Transmuted spotify request: %s", query.uuid)
