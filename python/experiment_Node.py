__author__ = 'mostlychris'
import socket, sys, messages
import decode_manager
from udp import *
from ack_handler import *

if (len(sys.argv) < 3):
    print("Usage: node.py {id} {num nodes}")
    exit(1)

me = int(sys.argv[1])
num_nodes = int(sys.argv[2])

ack_sender = AckSender("10.42.0.1")
rec = UdpReceiver(5000)
decoder = decode_manager.DecodeManager(num_nodes)
last_tid = -1

print("Started node at node", me, " with", num_nodes, "total nodes")

while True:
    # Get a message
    msg = bytearray(rec.rec(1024))
    tid = messages.get_test(msg)
    coeffs = messages.get_coeffs(msg, num_nodes)
    data = messages.get_data(msg)

    if (tid != last_tid):
        print("New test... Reseting.")
        decoder.reset()
        last_tid = tid

    new_decoded = decoder.addMessage(coeffs, data)

    # make sure the AP knows we can decode
    if coeffs[me] != 0 and decoder.can_decode(me):
        new_decoded.append(me)

    for decoded in new_decoded:
        ack_sender.ack(me, decoded)

