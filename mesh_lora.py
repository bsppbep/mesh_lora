# -*- coding: utf-8 -*-
"""LoRa network messenger

The class Messager if defined. Its behavior follows the flowchart is the
documentation.

Usage : 
    If you want to create a node that only forward the packets,
    then you should choose id_in_network=255
        >>> rfm95 = RFM95() # the sender/receiver
        >>> my_messenger = Messenger(rfm95, id_in_network=255)
        >>> my_messenger.start()

    If you want to create a node that can received and send its own packets,
    then you should choose id_in_network= 1 to 254. Here is how to send a packet
    from 1 to 2 :
        >>> rfm95 = RFM95() # the sender/receiver
        >>> my_messenger = Messenger(rfm95, id_in_network=1)
        >>> my_messenger.start()
        >>> my_messenger.post('hello world!', id_to = 2)
"""

import threading
import json
import time
import json
import random

from blinkt import set_pixel, show, clear

from setup_logger import logger


class Messenger:
    """A node of a LoRa meshed network. Store received messages in inbox.json
    You have to choose a unique id in the network (from 1 to 254).
    Use 255 if you want to define a simple node, that just forward the packets.

    Arguments:
        rfm95 {RFM95} -- The devide used to send and received packets

    Keyword Arguments:
        inbox_filename {str} -- the filename of the inbox (default: {'inbox.json'})
        id_in_network {int} -- my id in the network.  (default: {255})
    """

    def __init__(self, rfm95, inbox_filename='inbox.json', id_in_network=255):
        self.rfm95 = rfm95
        self.id_in_network = id_in_network
        self.inbox_filename = inbox_filename

        # Thread initialisation
        self._sender_receiver_thread = threading.Thread(
            name="LoRa messenger thread",
            target=self._sender_receiver, daemon=False)

        # Initialise the packets_to_send stack
        self.packets_to_send = []

        # Each time a packet is received, its header (id_to, id_from,
        # id_packet, flags) and time of receipt are stored in this set.
        self._received_packets_header_and_time = []

        # Two packets are considered identical, only if they have the
        # same (id_from, id_to, id_packet) and their reception is less than x seconds apart:
        self._packet_max_age = 3  # secondes

        # initialize the inbox file
        with open(self.inbox_filename, 'w') as inbox_file:
            json.dump([], inbox_file, indent=4)

    def start(self):
        """Start the thread"""
        self._sender_receiver_thread.start()

    def post(self, message, id_to=255):
        """Adds the packet to the list of packets to send."""
        # my id as sender
        id_from = self.id_in_network
        # choose a random id for the message
        id_message = random.randint(0, 254)
        # flag is not used so far
        flags = 0

        # build the packet
        packet = (id_from, id_to, id_message, flags, message.encode())
        # add to the packet_to_send stack
        self.packets_to_send.append(packet)

    def _sender_receiver(self):
        """Receive packet and send its own packet through rfm95."""
        while True:
            # if there is something to send, send it.
            if self.packets_to_send:
                packet_to_send = self.packets_to_send.pop()
                self._send_packet(packet_to_send)

                set_pixel(3, 127, 0, 255)
                show()
                time.sleep(0.3)
                set_pixel(3, 0, 0, 0)
                show()

            # if there is no packet to send
            else:
                received_packet = self._receive()

                # if nothing is received, continue
                if not received_packet:
                    continue

                # if the package has already been received, continue
                if self._packet_already_received(received_packet):
                    id_to, id_from, id_packet, flags = received_packet[:4]
                    logger.debug(
                        'message (id : {}) already received : ignoring'.format(id_packet))
                    continue

                # new packet received
                set_pixel(4, 0, 204, 0)
                show()
                time.sleep(0.3)
                set_pixel(4, 0, 0, 0)
                show()


                # else, keep a trace of the packet
                self._remember_we_got_that_packet(received_packet)

                # if the packet is for me, drop it in the inbox
                if self._is_packet_for_me(received_packet):
                    self.drop_in_inbox(received_packet)

                    # new packet received
                    set_pixel(5, 0, 204, 0)
                    show()
                    time.sleep(0.3)
                    set_pixel(5, 0, 0, 0)
                    show()

                # if the packet is not for me, or if it is
                # for everyone, forward it.
                if not(self._is_packet_for_me(received_packet)) \
                        or self._is_packet_for_everyone(received_packet):
                    self.packets_to_send.append(received_packet)

    def _receive(self):
        """Receive a packet and returns (id_from, id_to, id_packet, flags, message)"""
        # packet is a binary message. It starts with
        # the first 4 bytes are (id_from, id_to, id_packet, flags)
        # the rest is the message
        packet = self.rfm95.receive(with_header=True)
        if packet is None:
            return None
        id_to, id_from, id_packet, flags = packet[:4]
        message = packet[4:]
        logger.info('message (id : {}) from {} to {} received : {}'.format(
            id_packet, id_from, id_to, message))
        return id_from, id_to, id_packet, flags, message

    def _send_packet(self, packet):
        """Send an packet through RFM95"""
        id_from, id_to, id_packet, flags, message = packet
        try:
            # tx_header = (To,From,ID,Flags)
            self.rfm95.send(message, destination=id_to, node=id_from,
                identifier=id_packet, flags=flags)
            # self.rfm95.send(message, tx_header=(
            #     id_to, id_from, id_packet, flags))
        except Exception as error:
            logger.error(
                'sending of packet {} failed : {}'.format(id_packet, error))
        else:
            logger.info('message (id : {}) from {} to {} sent : {}'.format(
                id_packet, id_from, id_to, message))

    def _is_packet_for_me(self, packet):
        """Whether the packet is just for me for everyone (id_to = my_id)"""
        if self.id_in_network == 255:  # I am just a node
            return False

        _, id_to, _, _, _ = packet
        return id_to in [self.id_in_network, 255]

    def _is_packet_for_everyone(self, packet):
        """Whether the packet is for everyone (id_to = 255)"""
        _, id_to, _, _, _ = packet
        return id_to == 255

    def _packet_already_received(self, packet):
        """Whether the packet has been already received"""
        # get the header of the packet and the time of receipt
        id_to, id_from, id_packet, _ = packet[:4]

        # compare to all packets already received
        for old_id_from, old_id_to, old_id_packet, old_receipt_time in self._received_packets_header_and_time:
            if time.time() - old_receipt_time > self._packet_max_age:
                continue  # old packet is too old, and is ignored
            if (old_id_from, old_id_to, old_id_packet) == (id_from, id_to, id_packet):
                return True
        return False

    def _remember_we_got_that_packet(self, packet):
        """Add the packet id to the list of packet ids already received"""
        id_to, id_from, id_packet, _ = packet[:4]
        self._received_packets_header_and_time.append(
            (id_from, id_to, id_packet, time.time()))
        logger.info(
            'message (id : {}) stored in the list of packages already received.'.format(id_packet))

    def drop_in_inbox(self, packet):
        """Save packet in the inbox.json file"""
        # get the inbox by loading the json file
        with open(self.inbox_filename) as inbox_file:
            inbox = json.load(inbox_file)

        # add the new packet in the inbox
        id_from, id_to, id_packet, flags, message = packet
        inbox.append({
            'id_from': id_from,
            'id_to': id_to,
            'id_packet': id_packet,
            'flags': flags,
            'message': message.decode(),
            'receipt_time': time.time()})
        logger.info('new message (id : {}) in my inbox'.format(id_packet))

        # write on the json file the updated inbox.
        with open(self.inbox_filename, 'w') as inbox_file:
            json.dump(inbox, inbox_file, indent=4)


if __name__ == '__main__':
    # defines a simulated RFM95
    from simulated_RFM95 import RFM95
    rfm95 = RFM95()

    logger.info('start simulation')

    # Init the messenger. It's id withing the network is 1
    my_messenger = Messenger(rfm95, id_in_network=1)

    # Make it work 20 secondes
    my_messenger.start()
    my_messenger.post('hii', id_to=23)
    time.sleep(20)

    logger.info('end')
