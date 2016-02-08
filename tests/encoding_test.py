import messages
import time

# constants
NUM_NODES = 15
MSG_LEN = 10000

# testing procedure
nodes = [i for i in range(NUM_NODES)]

print("Creating data set...")
msgs = messages.gen_messages(NUM_NODES, MSG_LEN);

print("Combining all messages...")
combined = messages.combine(nodes, msgs)

c_nodes = messages.get_nodes(combined)
for i in range(NUM_NODES):
    assert i in c_nodes

print("Decoding messages...")
total = 0
for node in nodes:
    time1 = time.time()
    result = messages.extract(node, combined, msgs)
    time2 = time.time()
    assert result == msgs[node]
    total += time2-time1

print("Test passed\n\tavg decode time:", total/NUM_NODES)
