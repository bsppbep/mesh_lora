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

from mesh_lora.setup_logger import logger


class Interface(object):
    """A node of a LoRa meshed network. Store received messages in inbox.json
    You have to choose a unique id in the network (from 1 to 254).
    Use 255 if you want to define a simple node, that just forward the packets.

    Arguments:
        transceiver {transceiver} -- The devide used to send and received packets

    Keyword Arguments:
        inbox_filename {str} -- the filename of the inbox (default: {'inbox.json'})
        node {int} -- my id in the network.  (default: {255})
    """

    def __init__(self, transceiver, inbox_filename=None, node=255):
        self.transceiver = transceiver
        self.node = node
        self.inbox_filename = inbox_filename
        self._reception_callbacks = []
        self._sending_callbacks = []

        # Thread initialisation
        self._sender_receiver_thread = threading.Thread(
            name="LoRa Interface thread",
            target=self._sender_receiver, daemon=True)

        # Initialise the sending_queue stack
        self.sending_queue = []

        # Each time a packet is received, its header (id_to, id_from,
        # id_packet, flags) and time of receipt are stored in this set.
        self._received_packets_header_and_time = []

        # Two packets are considered identical, only if they have the
        # same (id_from, id_to, id_packet) and their reception is less than x seconds apart:
        self._packet_max_age = 3  # secondes

        # initialize the inbox file
        self._has_inbox = self.inbox_filename is not None
        if self._has_inbox:
            with open(self.inbox_filename, 'w') as inbox_file:
                json.dump([], inbox_file, indent=4)

    def add_on_reception_callback(self, callback):
        self._reception_callbacks.append(callback)
    
    def add_on_sending_callback(self, callback):
        self._sending_callbacks.append(callback)

    def start(self):
        """Start the thread"""
        self._sender_receiver_thread.start()

    def send(self, message, id_to=255, flags=0):
        """Adds the packet to the list of packets to send."""
        # my id as sender
        id_from = self.node
        # choose a random id for the message
        id_message = random.randint(0, 254)

        # build the packet (destination, node, identifier, flags)
        packet = (id_to, id_from, id_message, flags, message.encode())
        # add to the packet_to_send stack
        self.sending_queue.append(packet)

    def _sender_receiver(self):
        """Receive packet and send its own packet through transceiver."""
        while True:
            # if there is something to send, send it.
            if self.sending_queue:
                packet_to_send = self.sending_queue.pop()
                self._call_sending_callbacks(packet_to_send)
                self._send_packet(packet_to_send)

            # if there is no packet to send
            else:
                # try to receive something
                received_packet = self._receive()

                # if nothing is received, continue
                if not received_packet:
                    continue

                # if the packet has already been received, continue
                if self._packet_already_received(received_packet):
                    continue

                # else, keep a trace of the packet
                self._remember_the_packet(received_packet)

                # if the packet is for me, drop it in the inbox
                if self._is_packet_for_me(received_packet):
                    if self._has_inbox:
                        self.drop_in_inbox(received_packet)
                    self._call_reception_callbacks(received_packet)

                # if the packet is not for me, or if it is
                # for everyone, forward it.
                if not(self._is_packet_for_me(received_packet)) \
                        or self._is_packet_broadcasted(received_packet):
                    self.sending_queue.append(received_packet)

    def _call_reception_callbacks(self, packet):
        for callback in self._reception_callbacks:
            callback(packet)
    
    def _call_sending_callbacks(self, packet):
        for callback in self._sending_callbacks:
            callback(packet)

    def _receive(self):
        """Receive a packet and returns (id_to, id_from, id_packet, flags, message)"""
        # packet is a binary message. It starts with
        # the first 4 bytes are (id_to, id_from, id_packet, flags)
        # the rest is the message
        return self.transceiver.receive(with_header=True, timeout=1)

    def _send_packet(self, packet):
        """Send an packet through transceiver."""
        id_to, id_from, id_packet, flags, message = packet
        try:
            self.transceiver.send(message, destination=id_to, node=id_from,
                identifier=id_packet, flags=flags)
        except Exception as error:
            logger.error(
                'sending of packet {} failed : {}'.format(id_packet, error))

    def _is_packet_for_me(self, packet):
        """Whether I am the recipient of the packet.

        A packet is considered for me if id_to == my_id or id_to == 255 (broadcasted)
        """
        id_to = packet[0]
        return id_to in [self.node, 255]

    def _is_packet_broadcasted(self, packet):
        """Whether the packet is broadcasted (id_to == 255)"""
        id_to = packet[0]
        return id_to == 255

    def _packet_already_received(self, packet):
        """Whether the packet has been already received"""
        # get the header of the packet and the time of receipt
        id_to, id_from, id_packet, _ = packet[:4]

        # compare to all packets already received
        for old_id_to, old_id_from, old_id_packet, old_receipt_time in self._received_packets_header_and_time:
            if time.time() - old_receipt_time > self._packet_max_age:
                continue  # old packet is too old, and is ignored
            if (old_id_to, old_id_from, old_id_packet) == (id_to, id_from, id_packet):
                return True
        return False

    def _remember_the_packet(self, packet):
        """Add the packet id to the list of packet ids already received"""
        id_to, id_from, id_packet, _ = packet[:4]
        self._received_packets_header_and_time.append(
            (id_to, id_from, id_packet, time.time()))
        
    def drop_in_inbox(self, packet):
        """Save packet in the inbox.json file"""
        # get the inbox by loading the json file
        with open(self.inbox_filename) as inbox_file:
            inbox = json.load(inbox_file)

        # add the new packet in the inbox
        id_to, id_from, id_packet, flags, message = packet
        inbox.append({
            'id_to': id_to,
            'id_from': id_from,
            'id_packet': id_packet,
            'flags': flags,
            'message': message.decode(),
            'receipt_time': time.time()})


        # write on the json file the updated inbox.
        with open(self.inbox_filename, 'w') as inbox_file:
            json.dump(inbox, inbox_file, indent=4)


if __name__ == '__main__':
    # defines a simulated transceiver

    from mesh_lora.fake_transceiver import FakeTransceiver, World
    world = World()
    transceiver = FakeTransceiver(world)

    # Init the interface. It's id within the network is 1
    my_interface = Interface(transceiver, node=1)

    # Make it work 20 secondes
    my_interface.start()
    my_interface.send('hii', id_to=23)
    print('sent')
    time.sleep(2)

