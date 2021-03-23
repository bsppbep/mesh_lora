import time

from mesh_lora import Interface
from mesh_lora.fake_transceiver import FakeTransceiver, World
from mesh_lora.pubsub import Subscriber, Publisher


world = World()

transceiver_1 = FakeTransceiver()
transceiver_2 = FakeTransceiver()

world.spawn_transceiver(transceiver_1)
world.spawn_transceiver(transceiver_2)

interface_1 = Interface(transceiver_1, node=255)
interface_2 = Interface(transceiver_2, node=255)

interface_1.start()
interface_2.start()

pub = Publisher(interface_1, 'my_topic')
Subscriber(interface_2, 'my_topic', lambda x: print(x))

pub.publish('My message')

time.sleep(1)
