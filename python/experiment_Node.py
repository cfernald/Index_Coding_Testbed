__author__ = 'ryan'
import socket, sys, messages
from udp import *
from ack_handler import *

if (len(sys.argv) < 2):
    print "Usage: node.py {id}"
    exit(1)

me = int(sys.argv[1])

ack_sender = AckSender("127.0.0.1")
rec = UdpReceiver(5000)

sideInfo = dict()
while True:
    msg = bytearray(rec.rec(1024))
    data = messages.get_data(msg)
    nodes = messages.get_nodes(msg)

    if len(nodes) == 1:
        ack_sender.ack(me, nodes[0])
        sideInfo[nodes[0]] = data
    else:
        print "we haven't implemented decoding yet"
