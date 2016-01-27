import numpy as np
import math
import messages

'This is the file that contains the algorithm codes and determines with algorithm is being used'

def reduceMessages(msgs, acks):
    return roundRobin(msgs, acks)

def roundRobin(msgs, acks):
    'This method just identifies the the missing 1s along the diagnal'
    
    result = []

    for i in range(0, len(msgs)):
        if (acks[i][i] == 0):
            result.append(messages.format_msg([i], msgs[i]))

    return result


def APRankReduce(targetRank, sideInfoMatrix, tolerance):

    iteration = 0
    n = len(sideInfoMatrix)
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")
    m = len(sideInfoMatrix[0])
    projectionDistance = 100000 # initalized to a large value
    currentRank = n

    M = np.random.rand(n,m)
    oldM = M

    while currentRank>targetRank and projectionDistance>(tolerance/(n**3)): # and CheckInf<n-Rnk+5, in matlab script
        iteration += 1
        print(iteration)

        U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
        currentRank = 0
        for val in s:
            if val>tolerance: currentRank += 1
        S = np.diag(s)
        S[targetRank:, :] = 0 # killing all but targetRank many dimensions (projection onto the set of matrices with <=targetRank)
        # CheckInf = S(1) in matlab script


        M = np.dot(U, np.dot(S,V))
        projectionDistance = np.linalg.norm(oldM-M, ord=2) #L2 norm
        oldM = M

        # now project back to the set of matrices where all that changed was the don't cares
        for i in range(n):
            for j in range(m):
                if sideInfoMatrix[i,j] == 1:
                    M[i,j] = 1
                elif sideInfoMatrix[i,j] == 0:
                    M[i,j] = 0
                # else, leave the calculated matrix be. Changing these values makes it possible for M to not be the original rank, yes?

    return M


#test = np.array([[1, 2, 2, 0],[0, 1, 0, 0],[2, 0, 1, 0], [2, 2, 2, 1]])
#print APRankReduce(2,test,0.75)
