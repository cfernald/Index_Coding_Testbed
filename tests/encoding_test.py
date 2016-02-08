import messages

# constants
NUM_NODES = 20
MSG_LEN = 10

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
for node in nodes:
    result = messages.extract(node, combined, msgs)
    assert result == msgs[node]

print("Test passed")
