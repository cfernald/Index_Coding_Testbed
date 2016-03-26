__author__ = 'mostlychris'
import socket, sys, messages
from udp import *
from ack_handler import *

if (len(sys.argv) < 3):
    print("Usage: node.py {id} {num nodes}")
    exit(1)

me = int(sys.argv[1])
num_nodes = int(sys.argv[2])

ack_sender = AckSender("10.42.0.1")
rec = UdpReceiver(5000)
decoder = DecodeManager(num_nodes)
last_rid = -1

while True:
    # Get a message
    msg = bytearray(rec.rec(1024))
    rid = messages.get_round(msg)

    if (rid != last_rid):
        decoder.reset()
        last_rid = rid

    new_decoded = decoder.addMessage(msg)

    for decoded in new_decoded:
        ack_sender.ack(me, decoded)

