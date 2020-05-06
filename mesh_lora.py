
# coding:utf-8
"""Mesh LoRa communication
"""

import threading
import logging
import json
import os
import time

logger = logging.getLogger()

class Messenger:
    """A node of a LoRa meshed network. Store received messages in inbox.json

        Args:
            rfm95 (RFM95): The radio through which the message is sent
    """

    def __init__(self, rfm95, id_in_network=255):
        self.rfm95 = rfm95
        self.id_in_network = id_in_network

        # Thread initialisation
        self._sender_receiver_thread = threading.Thread(name="LoRa messenger thread",
                                                        target=self._sender_receiver, daemon=True)

        self.packets_to_send = []
        self.received_packets = set()
        self.inbox = []

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
                if received_packet in self.received_packets:
                    continue

                # else, keep a trace of the packet
                self.received_packets.add(received_packet)

                # if the packet is for me, drop it in the inbox
                if self.is_packet_for_me(received_packet):
                    self.drop_in_inbox(received_packet)
                # if the packet is not for me, re-send
                else:
                    self.packets_to_send.append(received_packet)

    def _receive(self):
        """Receive a packet and returns (id_from, id_to, id_message, flags, message)"""
        # packet is a binary message. It starts with
        # the first 4 bytes are (id_from, id_to, id_message, flags)
        # the rest is the message
        packet = self.rfm95.receive(with_header=True)
        if packet is None:
            return None
        id_from, id_to, id_message, flags = packet[:4]
        message = packet[4:]
        logger.info('message {} (from {} to {}) received : {}'.format(
            id_message, id_from, id_to, message))
        return id_from, id_to, id_message, flags, message

    def _send_packet(self, packet):
        """Send an packet through RFM95"""
        id_from, id_to, id_message, flags, message = packet
        try:
            # tx_header = (To,From,ID,Flags)
            self.rfm95.send(message, tx_header=(
                id_from, id_to, id_message, flags))
        except RuntimeError as error:
            logger.error(
                'sending of packet {} failed : {}'.format(id_message, error))
        else:
            logger.info('message {} (from {} to {}) sent : {}'.format(
                id_message, id_from, id_to, message))

    def is_packet_for_me(self, packet):
        if self.id_in_network == 255:  # I am just a node
            return False

        _, id_to, _, _, _ = packet
        return self.id_in_network == id_to

    def drop_in_inbox(self, received_packet):
        self.inbox.append(received_packet)
        logger.info('new message in my inbox')


def custom_log_setup():
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    log_file_name = "logs/mesh_lora_" + time.strftime("%Y-%m-%d") + ".log"
    file_handler = logging.FileHandler(log_file_name, mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    from simulated_RFM95 import RFM95

    logger = custom_log_setup()

    rfm95 = RFM95()
    logger.info('start')
    my_messenger = Messenger(rfm95, 1)
    my_messenger.start()
    time.sleep(10)
    logger.info('end')
