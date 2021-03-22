#-*- coding: utf-8 -*-
"""Mesh LoRa. 

A meshed LoRa network of communication beacons is being built here.
Each tag has a unique identifier in the network (between 1 and 254).
But we can also use one or more tags with the identifier 255. This tag
can only relay messages.
"""
import threading
import time

from mesh_lora.fake_transceiver import World, FakeTransceiver

world = World()
transceiver_1 = FakeTransceiver()
transceiver_2 = FakeTransceiver()
world.spawn_transceiver(transceiver_1)
world.spawn_transceiver(transceiver_2)

def wait_and_send(transceiver):
    my_message = b'Hello, world!'
    time.sleep(1)
    transceiver.send(my_message)

threading.Thread(name="sender", target=wait_and_send, args=(transceiver_1,)).start()
print('Message received by transciever 2:', transceiver_2.receive(timeout=5, with_header=True))