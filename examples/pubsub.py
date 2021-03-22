
from mesh_lora import Interface
from mesh_lora.fake_transceiver import FakeTransceiver, World
from mesh_lora.pubsub import Subscriber, Publisher

world = World()

transceiver_1 = FakeTransceiver()
transceiver_2 = FakeTransceiver()
transceiver_3 = FakeTransceiver()

world.spawn_transceiver(transceiver_1)
world.spawn_transceiver(transceiver_2)
world.spawn_transceiver(transceiver_3)

interface_1 = Interface(transceiver_1, node=255)
interface_2 = Interface(transceiver_2, node=255)
interface_3 = Interface(transceiver_3, node=255)

interface_1.start()
interface_2.start()
interface_3.start()

pub_1 = Publisher(interface_1, 'topic_1')
pub_2 = Publisher(interface_2, 'topic_2')

Subscriber(interface_2, 'topic_1', lambda x: print('[topic 1][interface 2]', x))
Subscriber(interface_3, 'topic_2', lambda x: print('[topic 2][interface 3]', x))

import time
time.sleep(0.1)
pub_1.publish('hi from interface 1')
time.sleep(0.1)
pub_2.publish('hi from interface 2')

time.sleep(1)