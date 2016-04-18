# This is a script to test the algorithms 
import sys, random, messages, algorithms, time
from decode_manager import DecodeManager
import encoding
import numpy as np
import matplotlib.pyplot as plt
import copy

def originalTest():
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


def sampleSideInfo(size, probOfDontCare):

    M = np.diag(np.ones(size))
    nonDiagEntries = 0.0
    dontCares = 0.0
    for i in range(size):
        for j in range(size):
            if i==j:
                continue # don't want to set the diagonals
            nonDiagEntries += 1
            if random.random() < probOfDontCare:
                M[i][j] = 2
                dontCares += 1

    # percentage of don't care entries, the matrix
    return (dontCares/nonDiagEntries, M)

# a square matrixSize x matrixSize
def timeSVDAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        last, best = algorithms.SVDAP(np.array(M)*9999, targetRank, max_iterations=200, resultPrecisionDecimals=8, return_analysis=True)
        runTime = time.time() - start
        results.append((percentDontCare, best[1], best[2], runTime))

    return results

def timeDirAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        Mr, rank, iterations = algorithms.dirAP(M, targetRank,resultPrecisionDecimals=8, max_iterations=200, return_analysis=True)
        runTime = time.time() - start
        results.append((percentDontCare, rank, iterations, runTime))

    return results

def timeLDGStartAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        print("start:",algorithms.thresholdRank( M))
        M = algorithms.expandLDG(algorithms.LDG(M), M)
        print("reduced/expanded:", algorithms.thresholdRank( M), "\n")
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        last, best = algorithms.SVDAP(np.array(M)*9999999999, targetRank, resultPrecisionDecimals=8, return_analysis=True)
        runTime = time.time() - start
        results.append((percentDontCare, last[1:], best[1:], runTime))

    return results

def timeLDGStartDirAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        print("start:",algorithms.thresholdRank( M))
        M = algorithms.expandLDG(algorithms.LDG(M), M)
        print("reduced/expanded:", algorithms.thresholdRank( M), "\n")
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        outM, rank, iterations = algorithms.dirAP(np.array(M), targetRank, startingMatrix=np.array(M)*9999999,resultPrecisionDecimals=8, return_analysis=True)
        print( rank , np.linalg.matrix_rank(M) )
        runTime = time.time() - start
        results.append((percentDontCare, rank, iterations, runTime))

    return results

results = []
def recurseAP(M, targetRank, step):
    start = time.time()
    Mr, rank, iterations = algorithms.SVDAP(M, targetRank, 0.001, maxTimeSeconds=2)
    runTime = time.time() - start
    results.append((rank,iterations, runTime))
    if rank > targetRank + 3:
        return
    percentageAchieved = 1-(rank - targetRank)/float(step)
    if percentageAchieved > 1:
        return
    recurseAP(Mr, step*percentageAchieved, step*2)


def testAPYah():
    #timeAP(100)
    #recurseAP(testMatrix(100,0.3)[1], 90, 10)
    algorithms.SVDAP(sampleSideInfo(100,0.3)[1], 30, 0.001)

    timingResults = {}
    for targetRank in range(5,96, 10):
        timingResults[targetRank] = timeSVDAP(targetRank)

    xAxis = [x for x in np.arange(0, 1, 0.1)]
    width = 0.03
    for i, r in enumerate(timingResults):
        percentDontCare = []
        rank = []
        iterations = []
        runTime =[]
        for result in timingResults[r]:
            percentDontCare.append(result[0])
            rank.append(result[1])
            iterations.append(result[2])
            runTime.append(result[3])
        iterationsAxis = [x+width for x in percentDontCare]
        runTimeAxis = [x+(width*2) for x in percentDontCare]

        fig = plt.figure(i)
        rank_bars = plt.bar(percentDontCare, rank, width, color='blue', align='center')
        iter_bars = plt.bar(iterationsAxis, iterations, width, color='red', align='center')
        #time_bars = ax.bar(runTimeAxis, runTime, width, color='green')
        plt.legend((rank_bars[0],iter_bars[0]), ('Rank','Iterations'))
        plt.autoscale(tight=True)
        plt.xlabel("Percentage of side info graph DC")
        plt.yticks(np.arange(0,200,10))
        plt.title("Target Rank {}".format(r))
        fig.savefig("Small Reals/{}.png".format(r))
        plt.close(i)

def testLDG():
	for i in range(0,100,10):
		percentDontCare, M = sampleSideInfo(10, i/100.0)
		print (np.linalg.matrix_rank(M), "\n\n")
		print (np.linalg.matrix_rank(algorithms.LDG(M)), "\n\n---------\n\n")
		print (np.linalg.matrix_rank(M), "\n\n")
		print (np.linalg.matrix_rank(algorithms.LDG(M)), "\n\n---------\n\n")
		raw_input()

def testLDGExpansion():
    for i in range(0,100,10):
        percentDontCare, M = sampleSideInfo(5, i/100.0)
        reducedM = algorithms.LDG(M)
        expandedM = algorithms.expandLDG(reducedM, M)
        print(M, "\n\n")
        print (np.array(reducedM), "\n\n")
        print (np.array(expandedM), "\n\n---------\n\n")

        #print np.linalg.matrix_rank(M), "\n\n"
        #print np.linalg.matrix_rank(reducedM), "\n"
        #print np.linalg.matrix_rank(expandedM), "\n\n---------\n\n"

def decodeTest():
	dm = DecodeManager(6)
	sideInfo = sampleSideInfo(6, 0.8)[1]
	m1 = encoding.EncodedMessage(b"message 1 asdf")
	m2 = encoding.EncodedMessage(b"message 2 asdf")
	m3 = encoding.EncodedMessage(b"message 3 asdf")
	m4 = encoding.EncodedMessage(b"message 4 asdf")
	m5 = encoding.EncodedMessage(b"message 5 asdf")
	m6 = encoding.EncodedMessage(b"message 6 asdf")
	messages = [m1, m2,m3,m4,m5, m6]
	encodedMessages = []
	
	for i, coeffs in enumerate(sideInfo):
		print(coeffs)
		encodedMessage = 0
		for j, m in enumerate(messages):
			encodedMessage = encodedMessage + (m * coeffs[j])
		encodedMessages.append(encodedMessage)
	decoded = None
	for i in range(len(sideInfo)):
		decoded = dm.addMessage(sideInfo[i], messages[i].toBytes(removeMarker=False))
		
		
	print(decoded)

decodeTest()

#testLDGExpansion()
# (sideInfoMatrix,startMatrix, targetRank, eig_size_tolerance,
#print dirAP(testMatrix(50,0.5)[1],  30)
#Mr, rank, steps = APRankReduce2(testMatrix(50, 0.5)[1], 30)
'''n=  m = 50
M = np.random.rand(20,20)
print(M)
print(np.linalg.matrix_rank(M))
Mr = np.around(M , decimals=4)
print(np.linalg.matrix_rank(np.around(M, decimals=4)))
print(Mr)'''

'''
ax = plt.subplot(111)
w = 0.3
ax.bar(x-w, y,width=w,color='b',align='center')
ax.bar(x, z,width=w,color='g',align='center')
ax.bar(x+w, k,width=w,color='r',align='center')
ax.xaxis_date()
ax.autoscale(tight=True)

plt.show()


'''



