import matplotlib.pyplot as plt
import pickle
import sys
from copy import deepcopy

data_file_name = sys.argv[1]
data_file = open(data_file_name, "rb")
data = pickle.load(data_file)

# load the data
ENCODE_ALGOS = data["Algos"]
num_algos = len(ENCODE_ALGOS)
msgs_sent = data["Msgs Sent"]
loss_prob = data["Loss"]
owner_loss = data["Msgs Lost by Owner"]

print(ENCODE_ALGOS)

# sort the messages
for i in range(num_algos):
    msgs_sent[i].sort()

# graph the data
colors = ['red', 'green', 'blue', 'black', 'yellow']

plt.figure(1)
for algo_index in range(num_algos):
    plt.plot(range(len(msgs_sent[algo_index])), msgs_sent[algo_index], colors[algo_index], label=ENCODE_ALGOS[algo_index])

plt.title("Number of Messages Sent")
plt.xlabel("Test number")
plt.ylabel("Number of Messages")
plt.legend()
plt.savefig('messages_sorted.png')
#plt.show()
plt.close()

print("creating based on loss prob")

plt.figure(1)
for algo_index in range(num_algos):
    loss_cp = deepcopy(owner_loss[algo_index])
    msgs_cp = deepcopy(msgs_sent[algo_index])
    
    loss_cp, msgs_cp = zip(*sorted(zip(loss_cp, msgs_cp)))


    plt.plot(loss_cp, msgs_cp, colors[algo_index], label=ENCODE_ALGOS[algo_index])

plt.title("Number of Messages Sent")
plt.xlabel("Loss probability")
plt.ylabel("Number of Messages")
plt.legend()
plt.savefig('messages_by_loss.png')
#plt.show()
plt.close()


msgs_saved = [1, 25, 11, 5, 6, 4, 7, 0, 0, 0, 2, 9, 0, 8, 1, 0, 24,  9, 15, 12, 26, 22, 8, 16, 4]

rr_msgs = []
for i in range(len(msgs_saved)):
    rr_msgs.append(msgs_sent[1][i] + msgs_saved[i])

plt.figure(1)
loss_cp = deepcopy(loss_prob[1])
msgs_cp = deepcopy(msgs_sent[1])

print(loss_cp)
 
loss_cp, msgs_cp, rr_msgs = zip(*sorted(zip(loss_cp, msgs_cp, rr_msgs)))
#del loss_cp[-3]
#del msgs_cp[-3]
#del rr_msgs[-3]

plt.plot(loss_cp, msgs_cp, colors[1], label=ENCODE_ALGOS[1])
plt.plot(loss_cp, rr_msgs, colors[0], label=ENCODE_ALGOS[0])

plt.title("Number of Messages Sent")
plt.xlabel("Loss probability")
plt.ylabel("Number of Messages")
plt.legend()
plt.savefig('messages_indirect.png')
#plt.show()
plt.close()





