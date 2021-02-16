#-*- coding: utf-8 -*-
"""Mesh LoRa. 

A meshed LoRa network of communication beacons is being built here.
Each tag has a unique identifier in the network (between 1 and 254).
But we can also use one or more tags with the identifier 255. This tag
can only relay messages.
"""

import time

from mesh_lora import Interface
from mesh_lora.fake_transceiver import FakeTransceiver, World
from mesh_lora.setup_logger import logger

def spin():
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

def run():
    world=World()
    # defines transceiver
    transceiver = FakeTransceiver(world)

    # start logger
    logger.info('start')

    # Initialize the messenger.
    # The id (between 1 and 254) must be unique in the network.
    # If you want the tag to act only as a relay, you can use id 255.
    # The id 255 does not need to be unique in the network.
    my_interface = Interface(transceiver, node=255)
    logger.info('Messenger id : {}'.format(my_interface.node))

    # Start
    my_interface.start()
    spin()

if __name__=='__main__':
    run()
