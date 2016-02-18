__author__ = 'ryan'

import udp
import socket
import ack_handler
import algorithms
import signal 
import sys
import messages
from time import sleep,time
import matplotlib.pyplot as plt

# Static Variables
nodes = sys.argv[1].split()
nodes = list(map(int, nodes))
nodes.sort()
PORT = 5000
MY_IP = '10.42.0.1'
MSG_LEN = 100
NUM_TESTS = 10

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

# set up stats
rounds = []
round_time = []
lost_msgs = []
lost_by_owner_msgs = []
avg_encode_time = []
msgs_sent = []

for test in range(NUM_TESTS):
    toSend = []
    rnd = 0
    lost = 0
    lost_by_owner = 0
    encodings = 0
    encode_time = 0
    sent = 0
    round_start = time()
    
    for i in range(0, len(nodes)):
        toSend.append(messages.format_msg([i], msgs[i]))

    while (len(toSend) > 0):
        rnd += 1
        for message in toSend:
            broadcaster.send(message, PORT)
            sent += 1

        sleep(0.025)
        toSend = algorithms.reduceMessages(msgs, acks.acks, "rr")

    round_stop = time()

    sleep(1)
    acks.reset()

    rounds.append(rnd)
    round_time.append((round_stop - round_start) * 1000)
    lost_msgs.append(lost)
    lost_by_owner_msgs.append(lost_by_owner)
    msgs_sent.append(sent)
    #avg_encode_time.append(encode_time/encodings)

acks.stop()

print("Rounds", rounds)
print("Round Times", round_time)
print("Msgs Lost", lost_msgs)
print("Msgs Lost by Owner", lost_by_owner_msgs)

plt.plot(round_time)
plt.title("Test Time")
plt.xlabel("Test number")
plt.ylabel("Time (ms)")
plt.savefig('test_time.png')

plt.plot(msgs_sent)
plt.title("Messages Sent")
plt.xlabel("Test number")
plt.ylabel("Number of messages")
plt.savefig('messages_sent.png')

print("Testing complete.")

