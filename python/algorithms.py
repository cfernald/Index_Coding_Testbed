import numpy as np
import math
import messages
import random

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

# in M, 2s are considered *. Will return a set of vectors where 1 entries should be included
def LDG(sideInfoMatrix):
	M = sideInfoMatrix # this shallow copies and mangles the original matrix (change to copy.deepcopy() if you want to retain sideInfoMatrix)
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
				print("successful merge: \n", M, "\n\n")
				break
		
		i += 1
	# end "for all rows" while loop
	
	return np.array(M)
		
	
#test = np.array([[1, 2, 2, 0],[2, 1, 2, 0],[0, 2, 1, 2], [2, 0, 0, 1]])
#print LDG(test)
