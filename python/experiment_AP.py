__author__ = 'ryan'

import udp
import socket
import thread
import ack_handler
from time import sleep,time

# Static Variables
messages = ["1"]
PORT = 5000
MY_IP = '127.0.0.1'

# setup the ack listener
acks = ack_handler.AckListener(len(messages))
acks.start()

# initial round
broadcaster = udp.UdpBroadcaster(MY_IP)
for message in messages:
    print "Sending Message:", message
    broadcaster.send(message, PORT)


unReceived = set(messages)
rounds = []

sleep(10)
acks.stop()

'''while len(unReceived)>1:
    cur = time()
    ack = ackSock.recvfrom(1024)
    if (ack != None):
        unReceived.remove(int(ack))
        rounds.append(unReceived)

    for message in set:
        print "Resending Message:", message
        broadcaster.send(message, PORT)


print len(rounds)
print rounds'''
