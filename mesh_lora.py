# -*- coding: utf-8 -*-
"""LoRa network messenger


"""

import threading
import json
import time
import json

from setup_logger import logger


class Messenger:
    """A node of a LoRa meshed network. Store received messages in inbox.json

        Args:
            rfm95 (RFM95): The radio through which the message is sent
    """

    def __init__(self, rfm95, inbox_filename='inbox.json', id_in_network=255):
        self.rfm95 = rfm95
        self.id_in_network = id_in_network
        self.inbox_filename = inbox_filename

        # Thread initialisation
        self._sender_receiver_thread = threading.Thread(
            name="LoRa messenger thread",
            target=self._sender_receiver, daemon=True)

        # Initialise the packets_to_send stack
        self.packets_to_send = []

        # Every time a packet is received, his id is store in that set
        self.received_packets_id = set()

        # initialize the inbox file
        with open(self.inbox_filename, 'w') as inbox_file:
            json.dump([], inbox_file, indent=4)

    def start(self):
        self._sender_receiver_thread.start()

    def _sender_receiver(self):
        """Receive packet and send its own packet through rfm95."""
        while True:
            # if there is something to send, send it.
            if self.packets_to_send:
                packet_to_send = self.packets_to_send.pop()
                self._send_packet(packet_to_send)

            # if there is no packet to send
            else:
                received_packet = self._receive()

                # if nothing is received, continue
                if not received_packet:
                    continue

                # if the package has already been received, continue
                if self._packet_already_received(received_packet):
                    continue

                # else, keep a trace of the packet
                self._remember_we_got_that_packet(received_packet)

                # if the packet is for me, drop it in the inbox
                if self._is_packet_for_me(received_packet):
                    self.drop_in_inbox(received_packet)

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
        id_from, id_to, id_packet, flags = packet[:4]
        message = packet[4:]
        logger.info('message (id : {}) from {} to {} received : {}'.format(
            id_packet, id_from, id_to, message))
        return id_from, id_to, id_packet, flags, message

    def _send_packet(self, packet):
        """Send an packet through RFM95"""
        id_from, id_to, id_packet, flags, message = packet
        try:
            # tx_header = (To,From,ID,Flags)
            self.rfm95.send(message, tx_header=(
                id_from, id_to, id_packet, flags))
        except RuntimeError as error:
            logger.error(
                'sending of packet {} failed : {}'.format(id_packet, error))
        else:
            logger.info('message (id : {}) from {} to {} sent : {}'.format(
                id_packet, id_from, id_to, message))

    def _is_packet_for_me(self, packet):
        if self.id_in_network == 255:  # I am just a node
            return False

        _, id_to, _, _, _ = packet
        return id_to in [self.id_in_network, 255]

    def _is_packet_for_everyone(self, packet):
        _, id_to, _, _, _ = packet
        return id_to == 255

    def _packet_already_received(self, packet):
        id_from, id_to, id_packet, flags = packet[:4]
        return id_packet in self.received_packets_id

    def _remember_we_got_that_packet(self, packet):
        id_from, id_to, id_packet, flags = packet[:4]
        self.received_packets_id.add(id_packet)

    def drop_in_inbox(self, packet):
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
            'message': message.decode()})
        logger.info('new message in my inbox')

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
    time.sleep(20)

    logger.info('end')
