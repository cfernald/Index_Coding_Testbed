__author__ = 'ryan'

import udp
import socket
from time import sleep,time
messages = [1,2,3]

ackSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ackSock.bind(("127.0.0.1", 5005))

# initial round
broadcaster = udp.UdpBroadcaster()
for message in messages:
    broadcaster.send(message)


unReceived = set(messages)
rounds = []
while len(unReceived)>1:
    cur = time.time()
    while time.time()-cur < 0.001:
        unReceived.remove(int(ackSock.recvfrom(1024)))
    rounds.append(unReceived)

print len(rounds)
print rounds