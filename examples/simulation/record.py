import time

from mesh_lora.nodes import Recorder, Printer
from mesh_lora.fake_transceiver import FakeTransceiver, World
from mesh_lora import Interface
from mesh_lora.pubsub import Publisher

world = World()

transceiver = FakeTransceiver()
world.spawn_transceiver(transceiver)
interface = Interface(transceiver, node=255)
interface.start()

Recorder(interface)

# publisher
transceiver_bis = FakeTransceiver()
world.spawn_transceiver(transceiver_bis)
interface_bis = Interface(transceiver_bis, node=255)
interface_bis.start()
pub = Publisher(interface_bis, 'my_topic')
pub.publish('My message')

time.sleep(0.5)