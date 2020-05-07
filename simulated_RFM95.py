import time
import random

from setup_logger import logger

class RFM95():
    """Fake communication devices of subclass of adafruit_rfm9x.RFM95

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
        pass

    def receive(self, timeout=0.5, keep_listening=True, with_header=False, rx_filter=255):
        time_until_next_message = random.uniform(0, 5)
        if time_until_next_message > timeout: # No message
            time.sleep(timeout)
            return None

        # else : a message !
        b_id_from = (random.randint(0,10)).to_bytes(1, 'big')
        b_id_to = (random.randint(0, 3)).to_bytes(1, 'big')
        # b_id_to = (255).to_bytes(1, 'big')
        b_id_message = (random.randint(0, 254)).to_bytes(1, 'big')
        b_flags = (0).to_bytes(1, 'big')
        
        packet = b'hi'
        if with_header:    
            packet = b_id_from+b_id_to+b_id_message+b_flags+packet

        time.sleep(time_until_next_message)
        logger.debug('packet received : {}'.format(packet))
        return packet


    def send(self, data, timeout=2.0, keep_listening=False, tx_header=(255, 255, 0, 0)):

        packet = (
            tx_header[0].to_bytes(1, 'big')
            + tx_header[1].to_bytes(1, 'big')
            + tx_header[2].to_bytes(1, 'big')
            + tx_header[3].to_bytes(1, 'big')
            + data)

        logger.debug('packet sent : {}'.format(packet))


if __name__=='__main__':
    rfm95 = RFM95()
    my_message = b'hello world'
    rfm95.send(my_message)
    print(rfm95.receive(timeout=5,with_header=True))
