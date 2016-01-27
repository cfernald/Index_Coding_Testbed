__author__ = 'ryan'

import udp
import socket
import ack_handler
import algorithms
import signal 
import sys
import messages
from time import sleep,time

# Static Variables
nodes = sys.argv[1].split()
nodes = list(map(int, nodes))
nodes.sort()
PORT = 5000
MY_IP = '127.0.0.1'
MSG_LEN = 100

print("Starting experiment with nodes: ", nodes)

# setup the ack listener
acks = ack_handler.AckListener(len(nodes))

# setup shutdown listener
def signal_handler(signal, frame):
    print("Shutting down...\n")
    acks.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# start ack listener
acks.start()

# initial round
broadcaster = udp.UdpBroadcaster(MY_IP)

# generate messages
msgs = messages.gen_messages(len(nodes), MSG_LEN)

toSend = []
for i in range(0, len(nodes)):
    toSend.append(messages.format_msg([i], msgs[i]))

while (len(toSend) > 0):
    for message in toSend:
        broadcaster.send(message, PORT)

    sleep(1)
    toSend = algorithms.reduceMessages(msgs, acks.acks)

acks.stop()

