__author__ = 'ryan'
import socket

me = 1

acknowledgerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 5005))

sideInfo = set()
while True:
    data, addr = sock.recvfrom(1024)
    if data==me:
        # redundancy, yo
        for i in range(10):
            acknowledgerSock.sendto(me, ("10.42.0.1", 5005))
    else:
        sideInfo.add(data)
