import time

from mesh_lora import Interface
from mesh_lora.pubsub import Subscriber


class Printer:
    def __init__(
            self, interface, asctime: bool = True):
        self.asctime = asctime
        self.interface = interface
        self.subscriber = Subscriber(self.interface, 'all', self.print)

    def print(self, x):
        if self.asctime:
            x = ''.join(('[', time.asctime(), '] ', x))
        print(x)

