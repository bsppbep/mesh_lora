
import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut

import os
import logging
import time

from setup_logger import logger

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

