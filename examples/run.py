# -*- coding: utf-8 -*-
"""Mesh LoRa. 

A meshed LoRa network of communication beacons is being built here.
Each tag has a unique identifier in the network (between 1 and 254).
But we can also use one or more tags with the identifier 255. This tag
can only relay messages.
"""

import time

from mesh_lora import Interface, Transceiver
from mesh_lora.utils import spin
from mesh_lora.nodes import ImmobilityDetector, Printer


interface = Interface(Transceiver(), node=255)
interface.start()
ImmobilityDetector(interface)
Printer(interface, 'all')
spin()
