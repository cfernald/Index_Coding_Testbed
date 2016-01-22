__author__ = 'ryan'

import udp
import socket
import thread
import ack_handler
import algorithms
import signal 
import sys
from time import sleep,time

# Static Variables
messages = ["0"]
PORT = 5000
MY_IP = '10.42.0.1'

# setup the ack listener
acks = ack_handler.AckListener(len(messages))
acks.start()

# setup shutdown listener
def signal_handler(signal, frame):
    print "Shutting down...\n"
    acks.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# initial round
broadcaster = udp.UdpBroadcaster(MY_IP)

toSend = messages
while (len(toSend) > 0):
    for message in toSend:
        print "Sending Message:", message
        broadcaster.send(message, PORT)

    sleep(1)
    toSend = algorithms.reduceMessages(messages, acks.acks)

acks.stop()

