from typing import Any

import kombu

from pipo.config import settings


class Singleton(type):
    """Singleton class."""

    _instances = {}

    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AMQPConnector(metaclass=Singleton):
    """Hosted AMQP connection manager.

    Attributes
    ----------
    __connection: kombu.Connection
        Handles a hosted AMQP connection.
    """

    __connection: kombu.Connection

    def __init__(self) -> None:
        user = settings.amqp.user
        password = settings.amqp.password
        broker_address = settings.amqp.broker_address
        virtual_host = settings.amqp.virtual_host

        amqp_url = f"amqps://{user}:{password}@{broker_address}/{virtual_host}"

        if not self.__connection:
            self.__start_connection(amqp_url)

    def __start_connection(self, connection_str: str) -> None:
        """Initialize a connection to a hosted AMQP message broker."""
        self.__connection = kombu.Connection(connection_str)

    @property
    def connection(self):
        return self.__connection
