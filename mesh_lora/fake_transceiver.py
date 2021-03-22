import time
import copy


class World:
    """A place where transciever meet and share packets
    """
    def __init__(self):
        self.transceivers = []

    def spawn_transceiver(self, transceiver):
        transceiver.world = self
        self.transceivers.append(transceiver)

    def on_emmision(self, packet):
        """Called by transciever when a packet is sent."""
        for transceiver in self.transceivers:
            transceiver._on_reception(packet)


class FakeTransceiver:
    """Fake communication devices of subclass of adafruit_rfm9x.RFM95
    https://circuitpython.readthedocs.io/projects/rfm9x/en/latest/api.html

    Example of how to use it:

    Send a fake message:
    >>> my_frm95 = RFM95()
    >>> my_rfm95.send("Hello world!") # Do nothing

    Receive a fake message:
    >>> my_rfm95 = RFM95()
    >>> my_rfm95.receive() # returns sometime something
    Hello world!

    """

    def __init__(self):
        self._listening = False
        self._last_packet = None
        self.world = None

    def _on_reception(self, packet):
        """Function called by world when a packet is sent"""
        if self._listening:
            self._last_packet = packet

    def receive(self, keep_listening=True, with_header=False, with_ack=False, timeout=None):
        self._listening = True
        start = time.perf_counter()
        while True:
            if timeout is not None:
                elapsed = time.perf_counter() - start
                if elapsed > timeout:
                    break
            if self._last_packet is not None:
                break
            time.sleep(0.001)

        packet = copy.deepcopy(self._last_packet)
        self._last_packet = None
        self._listening = keep_listening
        return packet

    def send(self, data, *, keep_listening=False, destination=None, node=None, identifier=None, flags=None):
        """destination,node,identifier,flags"""
        destination = destination or 255
        node = node or 255
        identifier = identifier or 0
        flags = flags or 0

        packet = (
            destination.to_bytes(1, 'big')
            + node.to_bytes(1, 'big')
            + identifier.to_bytes(1, 'big')
            + flags.to_bytes(1, 'big')
            + data)

        self._listening = False
        self.world.on_emmision(packet)
        self._listening = keep_listening


if __name__ == '__main__':
    import threading
    world = World()
    transceiver_1 = FakeTransceiver()
    transceiver_2 = FakeTransceiver()
    world.spawn_transceiver(transceiver_1)
    world.spawn_transceiver(transceiver_2)

    my_message = b'hello world'

    def wait_and_send():
        time.sleep(1)
        transceiver_1.send(my_message)

    threading.Thread(name="sender", target=wait_and_send).start()
    print(transceiver_2.receive(timeout=5, with_header=True))
