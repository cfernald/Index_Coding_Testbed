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
import pickle

# Static Variables
nodes = sys.argv[1].split()
log_dir = sys.argv[2]
nodes = list(map(int, nodes))
nodes.sort()
PORT = 5000
MY_IP = '10.42.0.1'
MSG_LEN = 512
NUM_TESTS = 100
CLEAN_DATA = True
CLEAN_FACTOR = 3
ENCODE_ALGO = "ldg"


print("Starting experiment with nodes: ", nodes, "using", ENCODE_ALGO)

# setup the ack listener
acks = ack_handler.AckListener(len(nodes))

# setup shutdown listener
def signal_handler(signal, frame):
    print("\nShutting down...\n")
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
tests = []
rounds = []
test_time = []
lost_msgs = []
lost_by_owner_msgs = []
avg_encode_time = []
msgs_sent = []

for test in range(NUM_TESTS):
    print("Starting experiment", test)
    rnd = 0
    lost = 0
    lost_by_owner = 0
    encodings = 0
    encode_time = 0
    sent = 0
    test_start = time()
    
    # first round is always round robin
    toSend = algorithms.reduceMessages(msgs, acks.acks, test, ENCODE_ALGO)

    while (len(toSend) > 0):
        rnd += 1

        #if (rnd > 20):
        #    print("spiking with nodes", messages.get_nodes(toSend[0]))

        for message in toSend:
            broadcaster.send(message, PORT)
            sent += 1

        sleep(0.025)
        for i in range(len(nodes)):
            if (acks.acks[i][i] == 1):
                lost_by_owner += 1

        toSend = algorithms.reduceMessages(msgs, acks.acks, test, "ldg")

    test_stop = time()

    print("Finished test", test, "with", rnd, "rounds in", (test_stop - test_start), "seconds")

    sleep(1)
    acks.reset()

    tests.append(test)
    rounds.append(rnd)
    test_time.append((test_stop - test_start) * 1000)
    lost_msgs.append(lost)
    lost_by_owner_msgs.append(lost_by_owner)
    msgs_sent.append(sent)
    #avg_encode_time.append(encode_time/encodings)

acks.stop()

if CLEAN_DATA:
    time_avg = sum(test_time)/len(test_time)
    print("Cleaning data...")
    i = 0
    removed = 0
    while (i < len(test_time)):
        if test_time[i] > (time_avg * CLEAN_FACTOR):
            del tests[i]
            del test_time[i]
            del msgs_sent[i]
            del lost_msgs[i]
            del lost_by_owner_msgs[i]
            removed += 1
        else:
            i += 1
            
    print("Removed", removed, "tests.")

#print("Rounds", rounds)
#print("Test Times", test_time)
#print("Msgs Sent", msgs_sent)
#print("Msgs Lost", lost_msgs)
#print("Msgs Lost by Owner", lost_by_owner_msgs)
print("******************************")
print("Avg Test Time", (sum(test_time)/len(test_time)))
print("Avg Msgs Sent", (sum(msgs_sent)/len(msgs_sent)))
print("Avg Lost by Owner", (sum(lost_by_owner_msgs)/len(lost_by_owner_msgs)))
print("******************************")

pickleInfo = {"Rounds":rounds, "Test Times":test_time, "Msgs Sent":msgs_sent, "Msgs Lost":lost_msgs,"Msgs Lost by Owner":lost_by_owner_msgs}
pickle.dump(pickleInfo, open("{}/results.pkl".format(log_dir),"wb"))


plt.plot(test_time)
plt.title("Test Time")
plt.xlabel("Test number")
plt.ylabel("Time (ms)")
plt.savefig('{}/test_time.png'.format(log_dir))
plt.close()

plt.plot(tests, msgs_sent, 'b', tests, lost_by_owner_msgs, 'r', tests, lost_msgs, 'g')
plt.title("Number of Messages")
plt.xlabel("Test number")
plt.ylabel("Number of messages")
plt.savefig('{}/messages.png'.format(log_dir))
plt.close()

print("Testing complete.")

