
import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut

import os
import logging
import time

formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

if not os.path.exists('logs'):
    os.makedirs('logs')

log_file_name = "logs/messenger_" + time.strftime("%Y-%m-%d") + ".log"

file_handler = logging.FileHandler(log_file_name, mode="w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(file_handler)


class RFM95(adafruit_rfm9x.RFM9x):
    """Communication device, subclass of adafruit_rfm9x.RFM9x

    Raspberry Pi    Adafruit GPS
    5V              Vin
    GND             GND
                    EN
    GPIO5           G0
    SPI0_SCLK       SCK
    SPI0_MISO       MISO
    SPI0_MOSI       MOSI
    SPI0_CE1_N      CS
    GPIO25          RST

    Example of how to use it:

    At the same time, on the sender
    >>> my_frm95 = RFM95()
    >>> my_rfm95.send("Hello world!")

    At the same time, on the receiver :
    >>> my_rfm95 = RFM95()
    >>> my_rfm95.receive()
    Hello world!

    For more information, read the doc of adafruit_rfm9x.RFM9x
    """

    def __init__(self):
        CS = DigitalInOut(board.CE1)
        RESET = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        adafruit_rfm9x.RFM9x.__init__(
            self, spi, CS, RESET, 868.0, baudrate=1000000)
        self.tx_power = 23
        self.enable_crc = True

