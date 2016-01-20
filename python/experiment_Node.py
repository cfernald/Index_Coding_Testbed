__author__ = 'ryan'
import socket, sys
from udp import *
from ack_handler import *

if (len(sys.argv) < 2):
    print "Usage: node.py {id}"
    exit(1)

me = sys.argv[1]

ack_sender = AckSender("10.42.0.1")

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(("127.0.0.1", 5005))
rec = UdpReceiver(5000)

sideInfo = set()
while True:
    data = rec.rec(1024)
    if data==me:
        print "Recieved my packet"
        # redundancy, yo
        for i in range(1):
            ack_sender.ack(me, data)
    else:
        sideInfo.add(data)
