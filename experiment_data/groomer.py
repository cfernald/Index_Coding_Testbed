import matplotlib.pyplot as plt
import pickle
import sys

data_file_name = sys.argv[1]
data_file = open(data_file_name, "rb")
data = pickle.load(data_file)

# load the data
ENCODE_ALGOS = data["Algos"]
num_algos = len(ENCODE_ALGOS)
msgs_sent = data["Msgs Sent"]

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
plt.savefig('messages.png')
#plt.show()
plt.close()


