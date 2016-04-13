import numpy as np
import math
import messages
import random
import copy
import time
import sys
import matplotlib.pyplot as plt

'This is the file that contains the algorithm codes and determines with algorithm is being used'

DONT_CARE = -42
def reduceMessages(msgs, acks, tid, algo="rr", desired_rank=0.75, eig_tolerance=0.00001):
    new_messages = []
    
    #print(acks)
    if algo == "rr":
        result = roundRobin(msgs, acks)
    if algo == "ldg":
        result = LDG(acks)
        #print(acks, "\n\n", result, "\n\n\n")
    if algo == "svdap":
        rank = np.linalg.rank(acks)
        result = SVDAP(acks, int(desired_rank * rank), eig_tolerance, 

    for i in range(len(result)):
        msg = messages.encode_row(result[i], msgs, tid)
        if msg != None:
            new_messages.append(msg)

    return new_messages


def roundRobin(msgs, acks):
    'This method just identifies the the missing 1s along the diagnal'
    matrix = []

    for i in range(len(acks)):
        if acks[i][i] == 1:
            row = [0] * len(msgs)
            row[i] = 1
            matrix.append(row)

    return matrix


# in M, 2s are considered *. Will return a set of vectors where 1 entries should be included
def LDG(sideInfoMatrix):
    M =copy.deepcopy(sideInfoMatrix) # this shallow copies and mangles the original matrix (change to copy.deepcopy() if you want to retain sideInfoMatrix)
    i = 0
    numNodes = len(M[0])


    while i < len(M): # while we haven't gone through every row (the number of rows changes as we reduce, which is why this is not a for loop)
        rowIndices_available = set(x for x in range(len(M)) if x!=i)
        thisRow = M[i]
        mergedRow = [] # really only manipulated in the while loop, but it needs to be scoped above as to add to the index code

        # while we haven't tried to merge all rows with rowsToSelectFrom[i] but itself
        while len(rowIndices_available) > 0:
            mergeRowIndex = random.sample(rowIndices_available, 1)[0] # randomly select something to try and merge
            rowToMerge = M[mergeRowIndex]
            mergedRow = []
            # iterate through the two rows and merge, if possible
            for j in range(numNodes):
                # one is a 0 and the other is a 1; this row cannot be merged
                if thisRow[j]+rowToMerge[j] == 1:
                    rowIndices_available.remove(mergeRowIndex)
                    break
                elif thisRow[j]+rowToMerge[j] == 0:
                    mergedRow.append(0)
                # both 2s, i.e. don't cares
                elif thisRow[j]+rowToMerge[j] == 4:
                    mergedRow.append(2)
                # a don't care and a 0
                elif thisRow[j]+rowToMerge[j] == 2:
                    if thisRow[j]==rowToMerge[j]:
                        print(M, "j: ", j, "\n", thisRow, "\n", rowToMerge, "\n", mergeRowIndex, "\n", mergedRow)
                        raw_input("error \n")
                        raise BaseException("debug: somehow two 1s were merged?")
                    mergedRow.append(0)
                    didAMerge = True
                # a 1 and a don't care
                elif thisRow[j]+rowToMerge[j] == 3:
                    mergedRow.append(1)
                else:
                    print(thisRow, rowToMerge, mergedRow)
                    raw_input("error \n")
            #end for

            # if we successfully merged the row
            if len(mergedRow) == numNodes:
                M[i] = mergedRow
                M = np.delete(M,mergeRowIndex,0)
                #print("successful merge: \n", M, "\n\n")
                break

        if len(mergedRow) == numNodes:
            i = 0
        else:
            i += 1
    # end "for all rows" while loop

    for i in range(len(M)):
        for j in range(len(M[0])):
            if M[i][j] == 2:
                M[i][j] = DONT_CARE

    return np.array(M).tolist()


def APRankReduce_old(targetRank, sideInfoMatrix, eig_size_tolerance):

    iteration = 0
    n = len(sideInfoMatrix)
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")
    m = len(sideInfoMatrix[0])
    projectionDistance = 100000 # initalized to a large value
    currentRank = n

    CheckInf = 0
    M = np.random.randint(100000, size=(n,m))
    oldM = M

    while currentRank>targetRank and projectionDistance>(eig_size_tolerance/(n**3)): #and CheckInf<n-currentRank+5: #, in matlab script
        iteration += 1
        print(iteration,"\n", M)

        U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
        currentRank = 0
        for val in s:
            if val>eig_size_tolerance: currentRank += 1
        #print "rank ^", currentRank, "\n\n"
        #raw_input()
        S = np.diag(s)
        S[targetRank:, :] = 0 # killing all but targetRank many dimensions (projection onto the set of matrices with <=targetRank)
        CheckInf = S[0][0] #in matlab script

        #print "cur rank:", np.linalg.matrix_rank(M)
        M = np.dot(U, np.dot(S,V))
        #print "rank after dotting:", np.linalg.matrix_rank(M)

        projectionDistance = np.linalg.norm(oldM-M, ord=2) #L2 norm
        print( projectionDistance)
        oldM = M

        # now project back to the set of matrices where all that changed was the don't cares
        for i in range(n):
            for j in range(m):
                if sideInfoMatrix[i,j] == 1:
                    M[i,j] = 1
                elif sideInfoMatrix[i,j] == 0:
                    M[i,j] = 0
                else:
                    M[i,j] = round(M[i,j],0)
                # else, leave the calculated matrix be. Changing these values makes it possible for M to not be the original rank, yes?

    return M

# 'D' being the region where the matrix has non-zeros on the diagonal, 0s from side info set properly
def projectToD(M, sideInfoMatrix, zeroThreshold=0.0001, roundPrecision=4):
    n = len(sideInfoMatrix)
    m = len(sideInfoMatrix[0])

    for i in range(n):
        for j in range(m):
            # if we need to include it and it's been zeroed out
            if sideInfoMatrix[i][j] == 1 and abs(M[i][j]) < zeroThreshold:
                M[i][j] = 1 # might set this to the average of the column, or something
            elif sideInfoMatrix[i][j] == 0:
                M[i][j] = 0
            elif roundPrecision != None:
                M[i][j] = round(M[i][j], roundPrecision)
    return M

def SVDAP(sideInfoMatrix, targetRank, eig_size_tolerance, maxTimeSeconds=2, resultPrecisionDecimals=4):
    debug = True

    iteration = 0
    n = len(sideInfoMatrix)
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")
    m = len(sideInfoMatrix[0])
    projectionDistance = 100000 # initalized to a large value
    currentRank = n

    CheckInf = 0
    M = np.random.rand(n,m)*9999999999 # 999999999999999999
    #M = np.ones(shape=(n,m))
    #M = np.diag(np.ones(n))
    #M = np.random.rand(n,m)
    oldM = M

    beginTime = time.time()
    while currentRank>targetRank and projectionDistance>(eig_size_tolerance/(n**3)): #and CheckInf<n-currentRank+5: #, in matlab script
        iteration += 1
        U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
        #for val in s:
        #    if val>eig_size_tolerance: currentRank += 1
        #print "rank ^", currentRank, "\n\n"
        S = np.diag(s)
        S[targetRank:, :] = 0 # killing all but targetRank many dimensions (projection onto the set of matrices with <=targetRank)
        CheckInf = S[0][0] #in matlab script


        M = np.dot(U, np.dot(S,V))
        projectionDistance = np.linalg.norm(oldM-M, ord=2) #L2 norm
        if debug:
            print("now rank reduced:\n", M)
            print("with rank:", np.linalg.matrix_rank(M))
            print(projectionDistance)

        oldM = M

        # now project back to the set of matrices where all that changed was the don't cares
        for i in range(n):
            for j in range(m):
                if sideInfoMatrix[i,j] == 1 and abs(M[i,j]) < eig_size_tolerance:
                    M[i,j] = 1 # might set this to the average of 
                elif sideInfoMatrix[i,j] == 0:
                    M[i,j] = 0
                #else:
                #    M[i,j] = round(M[i,j],0)
                # else, leave the calculated matrix be. Changing these values makes it possible for M to not be the original rank, yes?
        currentRank = np.linalg.matrix_rank(M)
        if time.time() - beginTime > maxTimeSeconds:
            break

        if debug:
            print("now side info corrected:\n", M)
            print("with rank:", currentRank)
            print("\n\n")
            raw_input()

    return (M*(10**resultPrecisionDecimals)).astype(int).tolist(), currentRank, iteration

def dirAP(sideInfoMatrix,startMatrix, targetRank, eig_size_tolerance, maxTimeSeconds=2, resultPrecisionDecimals=4):
    def eigenRankReduce(M, targetRank):
        eigenvalues, eigenvectors = np.linalg.eig(M)
        eigenvalues = map(lambda x : x if x>0 else 0, eigenvalues) #only positive or 0 eigenvalues (positive semi definite)
        eigenStuff = [eigenPair for eigenPair in zip(eigenvalues, eigenvectors)] # attaching each eigenvalue to it's eigenvector
        eigenStuff.sort(reverse=True)  # Sort eigenpairs in ascending order according to value of eigenvector
        # overwrite the variables with the sorted stuff
        for i in range(len(eigenStuff)):
            eigenvalues = eigenStuff[i][0]
            eigenvectors = eigenStuff[i][1]
        eigenvalues[targetRank:] = 0 # kill the least significant eigenvector directions
        eigM = np.diag(eigenvalues) # Eigenvalues of M as diagonal matrix
        return np.dot(eigenvectors, np.dot(eigM, np.transpose(eigenvectors)) ) # First point in region C

    M = startMatrix; # AP start point (in region D)
    iteration = 0
    n = len(sideInfoMatrix)
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")
    m = len(sideInfoMatrix[0])
    projectionDistance = sys.maxint # initalized to a large value
    currentRank = n
    M = projectToD(M, sideInfoMatrix)
    OutM=M
    tmpN=np.zeros(1,60)
    previousFDistanceAvg = sys.maxint # initialized to a large value
    while(currentRank>targetRank and projectionDistance>eig_size_tolerance/n^3):
        iteration += 1 # Iteration Number

        # Projection on region C
        M = eigenRankReduce(M, targetRank)

        # Projection on region D
        M = projectToD(M, sideInfoMatrix)
        OutM = M # This M maybe the optimal solution
        currentRank=np.linalg.matrix_rank(M) # Current optimal Index Code Length

        # Directional Projection
        M2 = M  # Second point (in region D)
        M = eigenRankReduce(M, targetRank)

        projectionDistance = np.linalg.norm(OutM-M, 2) # numpy does Frobenius norm by default, while matlab does l2
        NormF = np.linalg.norm(OutM-M2,'fro') # Frobenius distance of first and second points
        M=OutM+NormF**2 / np.trace(np.transpose(OutM-M) *(OutM-M2))*(M-OutM) # Fourth point

        # Check stopping criteria every 60 iterations
        NumN=(iteration-1 % 60) + 1
        tmpN[NumN]=NormF
        if NumN==60:
            ENormF=sum(tmpN)/60 # Average Frobenius distance in 60 interations
            if iteration>60 and (previousFDistanceAvg<ENormF+eig_size_tolerance/n):
                break

            previousFDistanceAvg=ENormF

    # Projection on region D
    return projectToD(M, sideInfoMatrix)

#test = np.array([[1, 2, 2, 0],[2, 1, 2, 0],[0, 2, 1, 2], [2, 0, 0, 1]])
#test2 = np.array([[1,2,2,2],[2,1,2,2],[2,2,1,2],[2,2,2,1]])

#res = APRankReduce2(test2, 1, 0.0001)
#print(res)
#print "with rank ", np.linalg.matrix_rank(res)


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
def timeAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        Mr, rank, iterations = SVDAP(M, targetRank, 0.001)
        runTime = time.time() - start
        results.append((percentDontCare, rank, iterations, runTime))

    return results


results = []
def recurseAP(M, targetRank, step):
    start = time.time()
    Mr, rank, iterations = SVDAP(M, targetRank, 0.001, maxTimeSeconds=2)
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
    SVDAP(sampleSideInfo(100,0.3)[1], 30, 0.001)

    timingResults = {}
    for targetRank in range(5,96, 10):
        timingResults[targetRank] = timeAP(targetRank)

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

# take a matrix and add additional rows (to equal the number of columns), keeping the rank as low as possible (greedily)
def expandLDG(M, sideInfoMatrix):
    def percentNonZero(row):
        if row is None:
            return 0
        return sum(1.0 for e in row if e==DONT_CARE) / len(row)

    n = len(M) # rows
    m = len(M[0]) # cols

    # a list with a row that has that position's column nonzero, and number of nonzeros close to 50%
    # so that we can keep M's diagonal nonzero by duplicating rows whenever possible (and thus keeping rank low)
    rowWithColSet =  [None for i in range(m)]
    for i in range(n):
        for j in range(m):
            currentRowOffset = abs(0.5 - percentNonZero(M[i]))
            cachedRowOffset = abs(0.5 - percentNonZero(rowWithColSet[j]))
            if M[i][j] != 0 and currentRowOffset < cachedRowOffset:
                rowWithColSet[j] = copy.deepcopy(M[i]) # if it has the row set, and is closer to 50% nonzeros, save it

    expandedSideInfo = []
    for row in rowWithColSet:
        if row is None:
            expandedSideInfo.append([0]*m)
        else:
            expandedSideInfo.append(row)

    expandedSideInfo = projectToD(expandedSideInfo, sideInfoMatrix)
    for i in range(m):
        if expandedSideInfo[i][i] == DONT_CARE:
                expandedSideInfo[i][i] = 1

    return expandedSideInfo

def testLDG():
	for i in range(0,100,10):
		percentDontCare, M = sampleSideInfo(10, i/100.0)
		print np.linalg.matrix_rank(M), "\n\n"
		print np.linalg.matrix_rank(LDG(M)), "\n\n---------\n\n"
		print (np.linalg.matrix_rank(M), "\n\n")
		print (np.linalg.matrix_rank(LDG(M)), "\n\n---------\n\n")
		raw_input()

def testLDGExpansion():
    for i in range(0,100,10):
        percentDontCare, M = sampleSideInfo(5, i/100.0)
        reducedM = LDG(M)
        expandedM = expandLDG(reducedM, M)
        print M, "\n\n"
        print np.array(reducedM), "\n\n"
        print np.array(expandedM), "\n\n---------\n\n"

        #print np.linalg.matrix_rank(M), "\n\n"
        #print np.linalg.matrix_rank(reducedM), "\n"
        #print np.linalg.matrix_rank(expandedM), "\n\n---------\n\n"

testAPYah()
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



