#-*- coding: utf-8 -*-
"""Mesh LoRa. 

A meshed LoRa network of communication beacons is being built here.
Each tag has a unique identifier in the network (between 1 and 254).
But we can also use one or more tags with the identifier 255. This tag
can only relay messages.
"""

import time
from setup_logger import logger

from mesh_lora import Messenger

from fake_RFM95 import FakeRFM95, World

logger.info('simulation started')

world = World()
# defines RFM95
rfm95_1 = FakeRFM95(world, uid =1)
my_messenger_1 = Messenger(rfm95_1, id_in_network=1)
my_messenger_1.start()
my_messenger_1.add_on_reception_callback(lambda packet:print('received by 1 : ', packet))
my_messenger_1.add_on_sending_callback(lambda packet:print('emmited by 1 : ', packet))


rfm95_2 = FakeRFM95(world, uid=2)
my_messenger_2 = Messenger(rfm95_2, id_in_network=2)
my_messenger_2.start()
my_messenger_2.add_on_reception_callback(lambda packet:print('received by 2 : ', packet))
my_messenger_2.add_on_sending_callback(lambda packet:print('emmited by 2 : ', packet))

my_messenger_1.post('hello', id_to=2)

