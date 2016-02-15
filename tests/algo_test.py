# This is a script to test the algorithms 
import sys, random, messages, algorithms, time

RUNS = 1000
MSG_LEN = 512
NUM_NODES = 15
LOSS = 0.9
ALGOS = ["rr", "ldg"]

print("Generating messages...")

rounds = [0] * len(ALGOS)
sent = [0] * len(ALGOS)
lost = [0] * len(ALGOS)
owner_lost = [0] * len(ALGOS)

print("Testing algorithms...")

for algo in range(len(ALGOS)):
    rand = random.Random()
    rand.seed(123456789)

    for i in range(RUNS):
        #print("Running round", i, "...")
        acks = [[0 for x in range(NUM_NODES)] for y in range(NUM_NODES)]
        for j in range(NUM_NODES):
            acks[j][j] = 1
        
        msgs = messages.gen_messages(NUM_NODES, MSG_LEN)
        toSend = []
        for j in range(len(msgs)):
            toSend.append(messages.format_msg([j], msgs[j]))

        while (len(toSend) > 0):
            rounds[algo] += 1
                
            for msg in range(len(toSend)):
                sent[algo] += 1
                for node in range(NUM_NODES):
                    msg_nodes = messages.get_nodes(toSend[msg])
                    if rand.random() > LOSS:
                        lacking = 0
                        for n in msg_nodes:
                            if acks[node][n] <= 1:
                                lacking += 1

                        if lacking <= 1:
                            for n in msg_nodes:
                                acks[node][n] = 2;

                    else:
                        lost[algo] += 1
                        if len(msg_nodes) == 1 and msg_nodes[0] == node:
                            owner_lost[algo] += 1

            toSend = algorithms.reduceMessages(msgs, acks, ALGOS[algo]) 
            
    print("*****************************************")        
    print("Algorithm:", ALGOS[algo])
    print("Avg Rounds:", rounds[algo] / RUNS)
    print("Avg Broacasts sent:", sent[algo] / RUNS)
    print("Avg Lost messages:", lost[algo] / RUNS)
    print("Avg Lost by owner:", owner_lost[algo] / RUNS)
    
    #print("Done.")

print("************* Testing Done **************")
