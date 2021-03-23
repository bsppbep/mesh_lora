# -*- coding: utf-8 -*-
"""Network Interface

The class Messager if defined. Its behavior follows the flowchart is the
documentation.

Usage : 
    If you want to create a node that only forward the packets,
    then you should choose node=255
        >>> transceiver = transceiver() # the sender/receiver
        >>> my_interface = Interface(transceiver, node=255)
        >>> my_interface.start()

    If you want to create a node that can received and send its own packets,
    then you should choose node= 1 to 254. Here is how to send a packet
    from 1 to 2 :
        >>> transceiver = transceiver() # the sender/receiver
        >>> my_interface = Interface(transceiver, node=1)
        >>> my_interface.start()
        >>> my_interface.post('hello world!', id_to = 2)
"""

import threading
import json
import time
import json
import random
from typing import Callable, Tuple

from mesh_lora.setup_logger import logger
from mesh_lora.common import Packet


class Interface:
    """Interface with the transciever.

    A node is identified on the network with an ID. This interface allows to use
    this node to send and receive packets.
    When a packet destined for this node is received, the interface calls the
    reception callbacks. To register a callback, use the method 
    `register_reception_callback`:

    >>> interface.register_reception_callback(my_callback)

    If the id of the node is 255, all packets triggers the callbacks.

    To send a packet, you have to call the `send` method with the recipient id:

    >>> interface.send('Hello, world!'.encode(), id_to=123)

    If id_to is 255, the packet is broadcasted.

    Example:
    >>> interface = Interface(transceiver, node=123)
    >>> interface.start()
    # Say hello to node 124.
    >>> interface.send('Hello, world!'.encode(), id_to=124)
    # register a callback that print messages received.
    >>> interface.register_reception_callback(
        lambda message, flags: print('received:', message, flags))

    Args:
        transceiver ([type]): The transciever #TODO: fix type.
        node (int, optional): The id of the node. Universal receiver is 255.
            Defaults to 255.
    """

    def __init__(self, transceiver, node: int = 255):
        self.transceiver = transceiver
        self.node = node
        self._reception_callbacks = []

        # Thread initialisation
        self._sender_receiver_thread = threading.Thread(
            name="LoRa Interface thread",
            target=self._sender_receiver, daemon=True)

        # Initialise the sending_queue stack
        self._sending_queue = []
        # Every time a packet is received, its header (id_to, id_from,
        # id_packet, flags) and time of receipt are stored in this list.
        self._received_packets_header_and_time = []

        # Two packets are considered identical, only if they have the
        # same (id_from, id_to, id_packet) and their reception is less than
        # x seconds apart:
        self._packet_max_age = 3  # seconds

    def register_reception_callback(
            self, callback: Callable[[bytes, int], None]) -> None:
        """Register a callback called when a packet is received.

        Args:
            callback (Callable[[bytes, int], None]): A callback that with args
                (payload, flags).
        """
        self._reception_callbacks.append(callback)

    def start(self):
        """Start the thread"""
        self._sender_receiver_thread.start()

    def send(self, payload, id_to=255, flags=0):
        """Send a packet.

        The packet is added to the stack of packets to be sent. The packets are
        then unstacked to be sent.

        Args:
            payload (bytes): Payload of the message.
            id_to (int, optional): The ID of the recipient. Defaults to 255.
            flags (int, optional): Flags of the message. Defaults to 0.
        """
        # my id as sender
        id_from = self.node
        # choose a random id for the message
        id_packet = random.randint(0, 254)
        # build the packet (destination, node, identifier, flags)
        tpacket = (id_to, id_from, id_packet, flags, payload)
        # add to the packet_to_send stack
        self._sending_queue.append(tpacket)

    def _decode_packet(
            self, packet: Packet) -> Tuple[int, int, int, int, bytes]:
        """Returns sender, recipient, packet id, flags and payload of a packet.

        Args:
            packet (Packet): The packet.

        Returns:
            Tuple[int, int, int, int, bytes]: (id_to, id_from,
            id_packet, flags, payload).
        """
        id_to, id_from, id_packet, flags = packet[:4]
        payload = packet[4:]
        return id_to, id_from, id_packet, flags, payload

    def _sender_receiver(self) -> None:
        """Receive packet and send its own packet through transceiver."""
        while True:
            # if there is something to send, send it.
            if self._sending_queue:
                packet_to_send = self._sending_queue.pop()
                # in order to ignore this packet if it go back
                self._remember_the_packet(packet_to_send)
                self._send_packet(packet_to_send)

            # if there is no packet to send
            else:
                # try to receive something
                received_bpacket = self._receive()

                # if nothing is received, continue
                if not received_bpacket:
                    continue

                # if packet received, decode it
                received_packet = self._decode_packet(received_bpacket)

                # if the packet has already been received, continue
                if self._packet_already_received(received_packet):
                    continue

                # else, keep a trace of the packet
                self._remember_the_packet(received_packet)

                # if the packet is for me, call the callbacks
                if self._is_packet_for_me(received_packet):
                    self._call_reception_callbacks(received_packet)

                # if the packet is not for me, or if it is
                # for everyone, forward it.
                if not(self._is_packet_for_me(received_packet)) \
                        or self._is_packet_broadcasted(received_packet):
                    self._sending_queue.append(received_packet)

    def _call_reception_callbacks(self, packet: Packet) -> None:
        """Call the reception callbacks."""
        _, _, _, flags, payload = packet
        for callback in self._reception_callbacks:
            callback(payload, flags)

    def _receive(self) -> Packet:
        """Wait for a packet to be received, and return it."""
        # packet is a binary message. It starts with
        # the first 4 bytes are (id_to, id_from, id_packet, flags)
        # the rest is the payload
        return self.transceiver.receive(with_header=True, timeout=0.1)

    def _send_packet(self, packet: Packet) -> None:
        """Send an packet through the transceiver."""
        id_to, id_from, id_packet, flags, payload = packet
        try:
            self.transceiver.send(payload, destination=id_to, node=id_from,
                                  identifier=id_packet, flags=flags)
        except Exception as error:
            logger.error(
                'sending of packet {} failed : {}'.format(id_packet, error))

    def _is_packet_for_me(self, packet: Packet) -> bool:
        """Whether I am the recipient of the packet.

        A packet is considered for me if id_to == self.node or
        id_to == 255 (broadcasted).

        Args:
            packet (Packet): The packet.

        Returns:
            bool: Whether I am the recipient of the packet.
        """
        id_to = packet[0]
        return id_to in [self.node, 255]

    def _is_packet_broadcasted(self, packet: Packet) -> bool:
        """Whether the packet is broadcasted (id_to == 255)"""
        id_to = packet[0]
        return id_to == 255

    def _packet_already_received(self, packet: Packet) -> bool:
        """Whether the packet has been already received"""
        # get the header of the packet and the time of receipt
        id_to, id_from, id_packet, _, _ = packet
        # compare to all packets already received
        for old_id_to, old_id_from, old_id_packet, old_receipt_time in self._received_packets_header_and_time:
            if time.time() - old_receipt_time > self._packet_max_age:
                continue  # old packet is too old, and is ignored
            if (old_id_to, old_id_from, old_id_packet) == (id_to, id_from, id_packet):
                return True  # from, to, and packet_id match
        return False

    def _remember_the_packet(self, packet: Packet) -> None:
        """Add the packet id to the list of packet ids already received"""
        id_to, id_from, id_packet, _, _ = packet
        self._received_packets_header_and_time.append(
            (id_to, id_from, id_packet, time.time()))


if __name__ == '__main__':
    # defines a simulated transceiver

    from mesh_lora.fake_transceiver import FakeTransceiver, World
    world = World()
    transceiver = FakeTransceiver()
    world.spawn_transceiver(transceiver)

    # Init the interface. It's id within the network is 1
    my_interface = Interface(transceiver, node=1)

    # Make it work 20 secondes
    my_interface.start()
    my_interface.send('hii', id_to=23)
    print('sent')
    time.sleep(2)
