__author__ = 'ryan'
import socket
from udp import *

me = "1"

acknowledgerSock = socket(AF_INET, SOCK_DGRAM)


#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(("127.0.0.1", 5005))
rec = UdpReceiver(5000)

sideInfo = set()
while True:
    data = rec.rec(1024)
    if data==me:
        # redundancy, yo
        for i in range(10):
            acknowledgerSock.sendto(me, ("10.42.0.1", 5005))
    else:
        sideInfo.add(data)
