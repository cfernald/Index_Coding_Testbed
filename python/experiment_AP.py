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
import statistics
from copy import deepcopy

# Static Variables
nodes = sys.argv[1].split()
log_dir = sys.argv[2]
nodes = list(map(int, nodes))
nodes.sort()

# Networking
PORT = 5000
MY_IP = '10.42.0.1'
# Dataset
MSG_LEN = 10000
NUM_TESTS = 15
# Data cleaning 
CLEAN_DATA = False # this should probably stay off
CLEAN_FACTOR = 3
# Timeouts
ROUNDS_TIMEOUT = 100
# Aglorithms used 
# "rr" = Round Robin
# "ldg" = least difference geedy
# "svdap" = SVD alternating projection
ENCODE_ALGOS = ["ldg"]
# Sleep times
SLEEP_BROADCASTS = 0.01
SLEEP_TESTS = 1.0
# save acks for debugging
SAVE_ACKS = True

# Code for expriments starts here
print("Starting experiment with nodes: ", nodes, "using", ENCODE_ALGOS)

# setup the ack listener
acks = ack_handler.AckListener(len(nodes))

# setup shutdown listener
def signal_handler(signal, frame):
    print("\nShutting down...\n")
    acks.stop()
    sys.stdout.flush()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# start ack listener
acks.start()

# Setup the udp broadcaster
broadcaster = udp.UdpBroadcaster(MY_IP)

# generate messages, 1 per nodes right now
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
msg_correlations = []
loss_avg = []
saved_acks = []
for algo_index in range(num_algos):
    tests.append([])
    rounds.append([])
    test_time.append([])
    lost_msgs.append([])
    lost_by_owner_msgs.append([])
    encode_time.append([])
    msgs_sent.append([])
    msgs_saved.append([])
    msg_correlations.append([])
    loss_avg.append([])

for test in range(NUM_TESTS):
    for algo_index in range(num_algos):
        algo = ENCODE_ALGOS[algo_index]
        print("Starting experiment", test, algo)
        sys.stdout.flush()
        rnd = 0
        lost = 0
        lost_by_owner = 0
        encodings = 0
        encode_time = 0
        sent = 0
        test_start = time()
        rank_diff = 0
        msg_correlation = 0
        loss = 0
    
        # first round is always round robin
        tid = ((test * num_algos) + algo_index) % 128
        toSend = algorithms.reduceMessages(msgs, acks.acks, tid, algo="rr")
        failed = False

        while (len(toSend) > 0 and not failed):
            rnd += 1

            #if (rnd > 20):
            #    print("spiking with nodes", messages.get_nodes(toSend[0]))

            for message in toSend:
                broadcaster.send(message, PORT)
                sleep(SLEEP_BROADCASTS)
                sent += 1

            sleep(0.25)
            for i in range(len(nodes)):
                if (acks.acks[i][i] == 1):
                    lost_by_owner += 1

            # calculate loss data
            if rnd == 1:
                received = deepcopy(acks.acks)
                for i in range(len(received)):
                    for j in range(len(received)):
                        if received[i][j] == 2:
                            received[i][j] = 1
                        else:
                            received[i][j] = 0

                col_avgs = []
                col_vars = []
                for i in range(len(nodes)):
                    col = []
                    for j in range(len(received)):
                        col.append(received[i][j])
                    col_avgs.append(sum(col)/len(col))
                    col_vars.append(statistics.variance(col))
                
                loss = 1 - sum(col_avgs)/len(col_avgs)
                msg_correlation = sum(col_vars)/len(col_vars)

                if SAVE_ACKS:
                    saved_acks.append(deepcopy(acks.acks))

            
            # calculate the rank RR would produce
            base_rank = 0
            for i in range(len(acks.acks)):
                if acks.acks[i][i] == 1:
                    base_rank += 1

            try:
                toSend = algorithms.reduceMessages(msgs, acks.acks, tid, algo=algo)
            except TimeoutError:
                failed = True
                break

            rank_diff += base_rank - len(toSend)
            if rank_diff < 0:
                print("WARNING: Sending out too many messages. RR:", base_rank,algo,len(toSend))
            if rnd > ROUNDS_TIMEOUT:
                failed = True

        test_stop = time()

        print("Finished test", test, algo, "with", rnd, "rounds in", (test_stop - test_start), "seconds with loss prob:", loss , "correlation:", msg_correlation, "msgs saved:", rank_diff, "tid:", tid)

        sleep(SLEEP_TESTS)
        acks.reset()

        if not failed:
            msgs_saved[algo_index].append(rank_diff)
            tests[algo_index].append(test)
            rounds[algo_index].append(rnd)
            test_time[algo_index].append((test_stop - test_start) * 1000)
            lost_msgs[algo_index].append(lost)
            lost_by_owner_msgs[algo_index].append(lost_by_owner)
            msgs_sent[algo_index].append(sent)
            msg_correlations[algo_index].append(msg_correlation)
            loss_avg[algo_index].append(loss)
            #avg_encode_time[algo_index].append(encode_time/encodings)
        else:
            print("Experiment timed out")

acks.stop()

for algo_index in range(num_algos):

    algo = ENCODE_ALGOS[algo_index]
    print("******************************")
    print("ENCODE ALGORITHM:", algo)

    if CLEAN_DATA:
        time_avg = sum(test_time)/len(test_time)
        #print("Cleaning data...")
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
    print("Avg loss probability", (sum(loss_avg[algo_index])/len(loss_avg[algo_index])))
    print("Avg message loss correlation", (sum(msg_correlations[algo_index])/len(msg_correlations[algo_index])))


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

colors = ['red', 'green', 'blue', 'black', 'yellow']
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
pickleInfo = {"Rounds":rounds, "Algos":ENCODE_ALGOS, "Test Times":test_time, "Msgs Sent":msgs_sent, "Msgs Lost":lost_msgs,"Msgs Lost by Owner":lost_by_owner_msgs,"Correlation":msg_correlations,"Loss":loss_avg}

pickle.dump(pickleInfo, open("{}/results.pkl".format(log_dir),"wb"))

if SAVE_ACKS:
    print("Pickling", len(saved_acks), "inital acks...")    
    pickle.dump(saved_acks, open("{}/acks.pkl".format(log_dir),"wb"))


print("Testing complete.")
sys.stdout.flush()

