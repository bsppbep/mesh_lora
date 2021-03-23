import time

from mesh_lora import Interface
from mesh_lora.pubsub import Subscriber


class Recorder:
    def __init__(
            self, interface, filename: str = 'record.txt', asctime: bool = True):
        self.filename = filename
        self.asctime = asctime
        self.interface = interface
        self.subscriber = Subscriber(self.interface, 'all', self.record)

    def record(self, x):
        if self.asctime:
            x = ''.join(('[', time.asctime(), '] ', x))
        with open(self.filename, 'a') as f:
            f.write(''.join((x, '\n')))
