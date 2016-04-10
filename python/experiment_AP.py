__author__ = 'ryan/chris'

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
from copy import deepcopy

# Static Variables
nodes = sys.argv[1].split()
log_dir = sys.argv[2]
nodes = list(map(int, nodes))
nodes.sort()
PORT = 5000
MY_IP = '10.42.0.1'
MSG_LEN = 512
NUM_TESTS = 50
CLEAN_DATA = False
CLEAN_FACTOR = 3
ENCODE_ALGOS = ["rr", "ldg"]


print("Starting experiment with nodes: ", nodes, "using", ENCODE_ALGOS)

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
num_algos = len(ENCODE_ALGOS)
tests = []
rounds = []
test_time = []
lost_msgs = []
lost_by_owner_msgs = []
encode_time = []
msgs_sent = []
msgs_saved = []
for algo_index in range(num_algos):
    tests.append([])
    rounds.append([])
    test_time.append([])
    lost_msgs.append([])
    lost_by_owner_msgs.append([])
    encode_time.append([])
    msgs_sent.append([])
    msgs_saved.append([])

for test in range(NUM_TESTS):
    for algo_index in range(num_algos):
        algo = ENCODE_ALGOS[algo_index]
        print("Starting experiment", test, algo)
        rnd = 0
        lost = 0
        lost_by_owner = 0
        encodings = 0
        encode_time = 0
        sent = 0
        test_start = time()
        rank_diff = 0
    
        # first round is always round robin
        tid = ((test * num_algos) + algo_index) % 128
        toSend = algorithms.reduceMessages(msgs, acks.acks, tid, algo="rr")

        while (len(toSend) > 0):
            rnd += 1

            #if (rnd > 20):
            #    print("spiking with nodes", messages.get_nodes(toSend[0]))

            for message in toSend:
                broadcaster.send(message, PORT)
                sleep(0.01)
                sent += 1

            sleep(0.25)
            for i in range(len(nodes)):
                if (acks.acks[i][i] == 1):
                    lost_by_owner += 1
            
            base_line = algorithms.reduceMessages(msgs, acks.acks, 0, algo="rr")
            toSend = algorithms.reduceMessages(msgs, acks.acks, tid, algo=algo)

            rank_diff += len(base_line) - len(toSend) 

        test_stop = time()

        print("Finished test", test, algo, "with", rnd, "rounds in", (test_stop - test_start), "seconds")

        sleep(1)
        acks.reset()

        msgs_saved[algo_index].append(rank_diff)
        tests[algo_index].append(test)
        rounds[algo_index].append(rnd)
        test_time[algo_index].append((test_stop - test_start) * 1000)
        lost_msgs[algo_index].append(lost)
        lost_by_owner_msgs[algo_index].append(lost_by_owner)
        msgs_sent[algo_index].append(sent)
        #avg_encode_time[algo_index].append(encode_time/encodings)

acks.stop()

print(tests)

for algo_index in range(num_algos):

    algo = ENCODE_ALGOS[algo_index]
    print("******************************")
    print("ENCODE ALGORITHM", algo)

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
    print("------------------------------")
    print("Avg Test Time", (sum(test_time[algo_index])/len(test_time[algo_index])))
    print("Avg number of round", (sum(rounds[algo_index])/len(rounds[algo_index])))
    print("Avg Msgs Sent", (sum(msgs_sent[algo_index])/len(msgs_sent[algo_index])))
    print("Avg Lost by Owner", (sum(lost_by_owner_msgs[algo_index])/len(lost_by_owner_msgs[algo_index])))
    print("Avg messages saved", (sum(msgs_saved[algo_index])/len(msgs_saved[algo_index])))


    plt.plot(test_time[algo_index])
    plt.title("Test Time")
    plt.xlabel("Test number")
    plt.ylabel("Time (ms)")
    plt.savefig('{}/{}_test_time.png'.format(log_dir, algo))
    plt.close()

    plt.plot(tests[algo_index], msgs_sent[algo_index], 'b', tests[algo_index], lost_by_owner_msgs[algo_index], 'r', tests[algo_index], lost_msgs[algo_index], 'g')
    plt.title("Number of Messages")
    plt.xlabel("Test number")
    plt.ylabel("Number of messages")
    plt.savefig('{}/{}_messages.png'.format(log_dir, algo))
    plt.close()

print("******************************")
print("Creating graph...")




colors = ['r', 'g', 'b']
plt.figure(1)
for algo_index in range(num_algos):
    plt.plot(tests[algo_index], msgs_sent[algo_index], colors[algo_index], label=ENCODE_ALGOS[algo_index])

plt.title("Number of Messages Sent")
plt.xlabel("Test number")
plt.ylabel("Number of Messages")
plt.legend()
plt.savefig('{}/messages.png'.format(log_dir))
#plt.show()
plt.close()

print("Pickling data...")
pickleInfo = {"Rounds":rounds, "Algos":ENCODE_ALGOS, "Test Times":test_time, "Msgs Sent":msgs_sent, "Msgs Lost":lost_msgs,"Msgs Lost by Owner":lost_by_owner_msgs}
pickle.dump(pickleInfo, open("{}/results.pkl".format(log_dir),"wb"))

print("Testing complete.")

