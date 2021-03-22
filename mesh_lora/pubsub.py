# -*- coding: utf-8 -*-
"""Pubsub implementation for Lora Mesh network.
"""

import pickle
from typing import Callable

from mesh_lora import Interface

PUBSUB_FLAG = 235


class Topic:
    """Topic.

    Args:
        topic_name (str): Name tof the topic
    """

    def __init__(self, topic_name: str):
        self.topic_name = topic_name


class Subscriber(Topic):
    """Subscribe to a topic.

    Args:
        interface (Interface): The interface used to send and receive.
        topic_name (str): The name of the topic to listen.
        callback (Callable[[str], None]): Called when a message is received on
            the topic. The arg is the message.

    Example:
        >>> from mesh_lora import Interface, Transceiver
        >>> interface = Interface(Transceiver(), node=255)
        >>> interface.start()
        >>> Subscriber(interface, 'my_topic', callback=print)
        # At this point, if a message is published in topic 'my_topic', the
        # message will be printed here
    """

    def __init__(
            self, interface: Interface, topic_name: str, callback: Callable):
        """Constructor."""
        super().__init__(topic_name)
        self.interface = interface
        func = self._check_pubsub(callback)  # decorate the function
        self.interface.register_reception_callback(func)

    def _check_pubsub(
            self, func: Callable[[str], None]) -> Callable[[bytes, int], None]:
        """Wrap function into a transceiver complient format."""
        def inner(payload: bytes, flags: int) -> None:
            if flags != PUBSUB_FLAG:  # check if it is "pubsub" complient
                return  # if not, do nothing
            topic_name, message = pickle.loads(payload)
            if topic_name != self.topic_name:  # check the topic name
                return  # if not topic name does not match, do nothing
            func(message)  # else, call the function
        return inner


class Publisher(Topic):
    """Register a publisher.

    Args:
        interface (Interface): The interface used to send and receive.
        topic_name (str): The name of the topic to listen.

    Example:
        >>> from mesh_lora import Interface, Transceiver
        >>> interface = Interface(Transceiver(), node=1)
        >>> interface.start()
        >>> pub = Publisher(interface, 'my_topic')
        >>> pub.publish('Hello, world!')
        # At this point, if a message is published in topic 'my_topic', the
        # message will be printed here
    """

    def __init__(self, interface: Interface, topic_name: str):
        super().__init__(topic_name)
        self.interface = interface

    def publish(self, message: str) -> None:
        """Publish a message on the topic.

        Args:
            message (str): The message to publish.
        """
        payload = pickle.dumps((self.topic_name, message))
        self.interface.send(payload, id_to=255, flags=PUBSUB_FLAG)
