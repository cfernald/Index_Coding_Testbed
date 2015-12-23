__author__ = 'ryan'

import udp
import socket
import thread
import ack_handler
import algorithms
from time import sleep,time

# Static Variables
messages = ["0"]
PORT = 5000
MY_IP = '127.0.0.1'

# setup the ack listener
acks = ack_handler.AckListener(len(messages))
acks.start()

# initial round
broadcaster = udp.UdpBroadcaster(MY_IP)

toSend = messages
while (len(toSend) > 0):
    for message in messages:
        print "Sending Message:", message
        broadcaster.send(message, PORT)

    sleep(1)
    toSend = algorithms.reduceMessages(messages, acks.acks)

acks.stop()

