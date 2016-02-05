# This is a script to test the algorithms 
import sys, random, messages, algorithms

RUNS = 100
MSG_LEN = 1000
NUM_NODES = 14
LOSS = 0.25

print("Generating messages...")
msgs = messages.gen_messages(NUM_NODES, MSG_LEN)

sent = 0
lost = 0
runs = 0
owner_lost = 0

for i in range(RUNS):
    print("Running round", i, "...")
    acks = [[0 for x in range(NUM_NODES)] for y in range(NUM_NODES)]
    msgs = messages.gen_messages(NUM_NODES, MSG_LEN)
    toSend = []
    for i in range(len(msgs)):
        toSend.append(messages.format_msg([i], msgs[i]))

    while (len(toSend) > 0):
        success = [True] * len(toSend) 
                
        for msg in range(len(toSend)):
            sent += 1
            for node in range(NUM_NODES):
                msg_nodes = messages.get_nodes(toSend[msg])
                if random.random() > LOSS:
                    lacking = 0
                    for n in msg_nodes:
                        if acks[node][n] == 0:
                            lacking += 1

                    if lacking <= 1:
                        for n in msg_nodes:
                            acks[node][n] = 1;

                else:
                    lost += 1
                    if len(msg_nodes) == 1 and msg_nodes[0] == node:
                        owner_lost += 1

        toSend = algorithms.reduceMessages(msgs, acks)          
    
    print("Done.")


print("************* Testing Done **************")
print("Broacasts sent:", sent)
print("Lost messages:", lost)
print("Lost by owner:", owner_lost)
 
