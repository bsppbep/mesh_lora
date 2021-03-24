import time
import threading
from collections import deque

import numpy as np
import envirophat

from mesh_lora import Interface
from mesh_lora.pubsub import Publisher


class ImmobilityDetector:
    """
    """

    def __init__(self, interface, threshold: float = 0.005, publish_rate: float = 1):
        self.interface = interface
        self.publisher = Publisher(self.interface, 'motionless')
        self.motion =  envirophat.motion
        self.threshold = threshold
        self.publish_rate = publish_rate
        self._buffer = deque([], maxlen=10)
        threading.Thread(name='IMU listener',
                         target=self._listener, daemon=True).start()
        threading.Thread(name='Motionless publisher',
                         target=self._publish_loop, daemon=True).start()

    def _listener(self):
        while True:
            acc = list(self.motion.accelerometer())  # [a_x, a_y, a_z]/9.81
            self._buffer.append(acc)
            time.sleep(0.1)

    def _publish_loop(self):
        while True:
            time.sleep(1/self.publish_rate)
            self.publisher.publish(str(self.is_motionless()))

    def is_motionless(self) -> True:
        return np.std(self._buffer) < self.threshold
