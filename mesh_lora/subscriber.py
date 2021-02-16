#-*- coding: utf-8 -*-
"""Mesh LoRa.
"""

class Message(object):
    def __init__(self, bstr):
        self.topic_name = 'topic_name'

class Topic(object):
    def __init__(self, topic_name, data_class):
        self.topic_name = topic_name

class Subscriber(Topic):
    def __init__(self, interface, topic_name, data_class, callback):
        super().__init__(self, topic_name, data_class, interface)

        self.topic_name = topic_name
        self.data_class = data_class
        self.interface = interface

        self.socket.register_reception_callback(callback)
      

class Publisher(Topic):
    def __init__(self, interface, topic_name, data_class):
        super().__init__(self, topic_name, data_class, interface)

        self.topic_name = topic_name
        self.data_class = data_class
        self.interface = interface

    def publish(self, msg):
        self.interface.publish



def my_func(packet):
    destination, node, identifier, flags, message = packet
    if flags == 1: # if topic complient
        message = Message(message)
        if message.topic_name == self.topic_name:
            print('yees')

        else:
            print('no... ignoring')


if __name__=='__main__':
    import time
    from setup_logger import logger

    from mesh_lora import Messenger

    from fake_RFM95 import FakeRFM95, World
    world = World()
    # defines RFM95
    rfm95_1 = FakeRFM95(world, uid =1)
    my_messenger_1 = Messenger(rfm95_1, id_in_network=1)
    my_messenger_1.start()
    my_messenger_1.add_on_reception_callback(lambda packet:print('received by 1 : ', packet))
    my_messenger_1.add_on_sending_callback(lambda packet:print('emmited by 1 : ', packet))


    rfm95_2 = FakeRFM95(world, uid=2)
    my_messenger_2 = Messenger(rfm95_2, id_in_network=2)
    my_messenger_2.start()
    my_messenger_2.add_on_reception_callback(lambda packet:print('received by 2 : ', packet))
    my_messenger_2.add_on_sending_callback(lambda packet:print('emmited by 2 : ', packet))
    Subscriber(my_messenger_2, 'topic_name')
    my_messenger_1.post('hello', id_to=2, flags=1)
