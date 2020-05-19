#-*- coding: utf-8 -*-
"""Mesh LoRa. 

A meshed LoRa network of communication beacons is being built here.
Each tag has a unique identifier in the network (between 1 and 254).
But we can also use one or more tags with the identifier 255. This tag
can only relay messages.
"""

import time

from mesh_lora import Messenger
from setup_logger import logger

# If you run this code on a module that does not have an
# RFM95 module, you can use a simulation of the RFM95 module.
simulation = True

if simulation:
    from simulated_RFM95 import RFM95
else:
    from RFM95 import RFM95

# defines RFM95
rfm95 = RFM95()

# start logger
logger.info('start')

# Initialize the messenger.
# The id (between 1 and 254) must be unique in the network.
# If you want the tag to act only as a relay, you can use id 255.
# The id 255 does not need to be unique in the network.
my_messenger = Messenger(rfm95, id_in_network=255)

# Make it work 60 secondes
my_messenger.start()
time.sleep(60)

logger.info('end')