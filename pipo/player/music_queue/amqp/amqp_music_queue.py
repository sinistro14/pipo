from typing import Any, Iterable, Optional

import kombu

from pipo.config import settings
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.amqp.amqp_connector import AMQPConnector
from pipo.player.music_queue.music_queue import MusicQueue


class AMQPMusicQueue(MusicQueue):
    """Cloud hosted AMQP message broker as music queue.

    Attributes
    ----------
    _connection: amqp_connector.AMQPConnector
        Hosted AMQP connection.
    _queue: kombu.Queue
        Queue music messages to retrieve by rotation key.
    _exchange: kombu.Queue
        Exchange to publish music messages.
    """

    __connection: kombu.Connection
    __audio_fetch_queue: kombu.Queue
    __audio_queue: kombu.Queue

    _audio_fetch_channel_pool: kombu.connection.ChannelPool
    _audio_channel_pool: kombu.connection.ChannelPool

    def __init__(self) -> None:
        audio_fetch_channel_pool, audio_channel_pool = self.__initialize()
        super().__init__(
            settings.player.queue.local.prefetch_limit,
            audio_fetch_channel_pool,
            audio_channel_pool,
        )

    def __initialize(self):
        # Connection initialization
        self.__connection = AMQPConnector().connection()
        audio_fetch_channel_pool = kombu.connection.ChannelPool(
            limit=settings.player.queue.amqp.channel_pool_limit
        )
        audio_channel_pool = kombu.connection.ChannelPool(
            limit=settings.player.queue.amqp.channel_pool_limit
        )

        # Default queues to preserve publish data
        self.__audio_fetch_queue = kombu.Queue(
            name=settings.player.queue.amqp.audio_fetch.queue_name,
            exchange=settings.player.queue.amqp.audio_fetch.exchange_type,
            routing_key=settings.player.queue.amqp.audio_fetch.routing_key,
        )
        self.__audio_queue = kombu.Queue(
            name=settings.player.queue.amqp.audio.queue_name,
            exchange=settings.player.queue.amqp.audio.exchange_name,
            routing_key=settings.player.queue.amqp.audio.routing_key,
        )
        return audio_fetch_channel_pool, audio_channel_pool

    def _add(self, music: str) -> None:
        """Add item to queue."""
        self.__push_messages(
            channel_pool=self._audio_channel_pool,
            exchange_name=settings.player.queue.amqp.audio.exchange_name,
            exchange_type=settings.player.queue.amqp.audio.exchange_type,
            routing_key=settings.player.queue.amqp.audio.routing_key,
            sources=[music],
        )

    def _get(self) -> Optional[str]:
        """Get queue item."""
        return self.__get_messages(
            channel_pool=self._audio_channel_pool,
            queue_name=settings.player.queue.amqp.audio.queue_name,
            target_exchange_name=settings.player.queue.amqp.audio.exchange_name,
            routing_key=settings.player.queue.amqp.audio.routing_key,
        )[0]

    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        self.__push_messages(
            channel_pool=self._audio_fetch_channel_pool,
            exchange_name=settings.player.queue.amqp.audio_fetch.exchange_name,
            exchange_type=settings.player.queue.amqp.audio_fetch.exchange_type,
            routing_key=settings.player.queue.amqp.audio_fetch.routing_key,
            sources=sources,
        )

    def _clear(self) -> None:
        """Clear queue."""
        self.__audio_fetch_queue.purge()
        self.__audio_queue.purge()

    def get_all(self) -> Any:
        """Get enqueued music."""
        return self.__get_messages(
            channel_pool=self._audio_channel_pool,
            queue_name=settings.player.queue.amqp.audio.queue_name,
            target_exchange_name=settings.player.queue.amqp.audio.exchange_name,
            routing_key=settings.player.queue.amqp.audio.routing_key,
            list_all=True,
        )

    def fetch_queue_size(self) -> int:
        """Fetch queue size."""
        return len(
            self.__get_messages(
                channel_pool=self._audio_fetch_channel_pool,
                queue_name=settings.player.queue.amqp.audio_fetch.queue_name,
                target_exchange_name=settings.player.queue.amqp.audio_fetch.exchange_name,
                routing_key=settings.player.queue.amqp.audio_fetch.routing_key,
                ack=False,
                list_all=True,
            )
        )

    def audio_queue_size(self) -> int:
        """Audio queue queue size."""
        return len(
            self.__get_messages(
                channel_pool=self._audio_channel_pool,
                queue_name=settings.player.queue.amqp.audio.queue_name,
                target_exchange_name=settings.player.queue.amqp.audio.exchange_name,
                routing_key=settings.player.queue.amqp.audio.routing_key,
                ack=False,
                list_all=True,
            )
        )

    def __get_messages(
        self,
        channel_pool: kombu.connection.ChannelPool,
        queue_name: str,
        target_exchange_name: str,
        routing_key: str,
        ack: bool = True,
        list_all: bool = False,
    ) -> list:
        """Fetch queue messages.

        Parameters
        ----------
        channel_pool: kombu.connection.ChannelPool
            Channel pool to acquire a new channel.
        queue_name: str
            Queue name to fetch messages.
        target_exchange_name: str
            Target exchange where messages were pushed from.
        routing_key: str
            Message routing key.
        ack: bool
            Ack recieved messages.
        list_all: bool
            List all messages in queue.
        """
        try:
            channel_pool.acquire(block=settings.player.queue.amqp.block)
        except kombu.exceptions.LimitExceeded:
            pass
        except RuntimeError:
            pass
        else:
            messages_list = []
            with self.__connection.channel() as channel:
                ephemeral_queue = kombu.Queue(
                    name=queue_name,
                    exchange=target_exchange_name,
                    routing_key=routing_key,
                    channel=channel,
                )
                amqp_message = ephemeral_queue.get()
                while amqp_message:
                    if amqp_message:
                        messages_list.append(amqp_message.decode())
                        if ack:
                            amqp_message.ack()
                    amqp_message = ephemeral_queue.get() if list_all else None

            channel_pool.release()
            return messages_list

    def __push_messages(
        self,
        channel_pool: kombu.connection.ChannelPool,
        exchange_name: str,
        exchange_type: str,
        routing_key: str,
        sources: list,
    ) -> None:
        """Publish messages to exchange.

        Parameters
        ----------
        channel_pool: kombu.connection.ChannelPool
            Channel pool to acquire a new channel.
        exchange_name: str
            Exchange name to push messages.
        exchange_type: {'direct', 'topic'}
            Message route mechanism.
        routing_key: str
            Message routing key.
        sources: list
            List of messages to send.
        """
        try:
            channel_pool.acquire(block=settings.player.queue.amqp.block)
        except kombu.exceptions.LimitExceeded:
            pass
        except RuntimeError:
            pass
        else:
            with self.__connection.channel() as channel:
                exchange = kombu.Exchange(
                    name=exchange_name,
                    type=exchange_type,
                    durable=True,
                    channel=channel,
                )
                with self.__connection.Producer(
                    serializer=settings.player.queue.amqp.serializer
                ) as producer:
                    for source in sources:
                        producer.publish(
                            source, routing_key=routing_key, exchange=exchange
                        )
            channel_pool.release()
