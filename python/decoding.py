__author__ = 'ryan'

from encoding import AppendEncoding
import time

# adapted from https://martin-thoma.com/solving-linear-equations-with-gaussian-elimination/
def gauss(A):
    n = len(A) # rows
    m = len(A[0]) # columns

    if n>m:
        print("more rows than columns, oh no")
        quit()

    #deoodingSteps will store the linear combination of the encoded messages needed to get to the state of a row of A
    #in a particular row of decodingSteps, the first entry represents the coefficient for the first encoded message,
    #the second entry for the second message, and so forth
    decodingSteps = []
    for k in range(0, n):
        decodingSteps.append([0]*n)
        decodingSteps[k][k] = 1 # initialize the diagonal to 1s because you start with just one of each of the encoded messages in A

    # for each row i
    for i in range(0, n):
        # Search for maximum in this column
        maxEl = abs(A[i][i])
        maxRow = i
        for k in range(i+1, n):
            if abs(A[k][i]) > maxEl:
                maxEl = abs(A[k][i])
                maxRow = k

        # Swap maximum row with current row (column by column)
        for k in range(i, m): #upper bound was n+1 before? even assuming a square matrix, why +1?
            tmp = A[maxRow][k]
            A[maxRow][k] = A[i][k]
            A[i][k] = tmp

        # swap the decodingSteps rows, too
        for k in range(0,n):
            tmp = decodingSteps[maxRow][k]
            decodingSteps[maxRow][k] = decodingSteps[i][k]
            decodingSteps[i][k] = tmp

        # we won't be able to cancel anything with this row
        if A[i][i] == 0:
            continue

        # Make all rows below this one 0 in current column
        curRowMult = A[i][i] # doesn't change for the rows below
        for k in range(i+1, n):
            pivotMult = A[k][i]

            # don't reduce this row if it is already reduced
            if pivotMult == 0:
                continue
            # update all columns of the reduced row
            for j in range(i, m):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] = A[k][j]*curRowMult - A[i][j]*pivotMult

            # update all columns of the decodingSteps
            for j in range(0, n):
                decodingSteps[k][j] = decodingSteps[k][j]*curRowMult  -  decodingSteps[i][j]*pivotMult

        #print(A, "\n", decodingSteps, "\n\n")

    for i in range(n-1, -1, -1):
        x[i] = A[i][n]/A[i][i]
        for k in range(i-1, -1, -1):
            A[k][n] -= A[k][i] * x[i]
    return A, decodingSteps

# this just works with int/long (need to adapt for data structure)
# and assumes only positive values
def efficientMult(a, b):

    def log2(n):
        if n<1:
            return None
        log = 0
        runningComparison = 1
        while True:
            if runningComparison == n:
                return log, 0
            if runningComparison > n:
                return log-1, n-(runningComparison>>1)
            runningComparison <<= 1
            log += 1
        # returns floor(log), remainder

    if a<0 or b<0:
        return None

    # want a to be the bigger
    if a < b:
        tmp = a
        a = b
        b = tmp
    orig = a
    shifts, adds = log2(b)
    print(shifts, adds)
    a <<= shifts
    for i in range(adds):
        a+=orig
    return a


# within a single round, where we recieve a set of encoded messages, decode with row reduction (assumes single pieces of side information
# already subtracted
def decodeWithRR(coefs, encodedMessages):

    reduced, steps = gauss(coefs)
    decodables = []
    for i, row in enumerate(reduced):
        canDecode = False
        divideBy = 0
        msgIndex = -1
        # if theres a single nonzero value in a row, we can decode (but have to divide in case that single value is not 1!)
        for j, columnVal in enumerate(row):
            if canDecode and columnVal != 0:
                canDecode = False
                break
            if not canDecode and columnVal != 0:
                canDecode = True
                divideBy = columnVal
                msgIndex = j

        if canDecode:
            # to decode: (index into reduced matrix, num of message you will recover, the multiple of the message you intend to recover)
            decodables.append((i,msgIndex, divideBy))

    idToMessage = {}
    for reducedRow, msg, divideBy in decodables:
        message = 0
        # eMsgNum is the index of the encoded message in the linear combination to recover the original message
        for eMsgNum, multBy in enumerate(steps[reducedRow]):
            message += encodedMessages[eMsgNum]*multBy
        # we got message to be a multiple of the intended message, now lets get the actual message
        idToMessage[msg] = message / divideBy

    return idToMessage





# row reducing by hand (especially the decodingSteps part) is a pain
def sanityCheck():
    A = [[0,2,1,-8],[1,-2,-3,0],[-1,1,2,3]]
    expectedReduced = [[1,-2,-3,0], [0,2,1,-8],[0,0,-1,-2]]
    expectedSteps = [[0,1,0],[1,0,0],[1,2,2]]
    reducedA, steps = gauss(A)
    assert(reducedA==expectedReduced)
    assert(steps==expectedSteps)



#A = [[11,20,30,40,50], [2,4,6,8,10], [1,2,3,4,5], [1,0,0,0,0]]
#print(gauss(A))
def sanityCheck2():
    msg1 = AppendEncoding("Hello, I am message1! I'm excited about it!")
    msg2 = AppendEncoding("Hello, I am message2! I'm ... okay about it")
    msg3 = AppendEncoding("I can't be decoded")
    combined1 = msg1*2 + msg2*3
    combined2 = msg1
    coefs = [[2,3,0],[0,1,0]] # combined is 2 of msg1 and 3 of msg2, and we'll send message 2 in order to recover both
    encodedMessages = [combined1.getEncoding(), msg2.getEncoding()]
    print(AppendEncoding(decodeWithRR(coefs,encodedMessages)[1], True))

def testMult():
    a = 12341239487398273498273409872123908743250983245982374598324509827345987234509872345987213312398712309187233498723498723049872349872340982734987234982734
    b = 512
    start = time.time()
    r1 = a*b
    print("regular mult: ", time.time()-start)

    start = time.time()
    r2 = efficientMult(a,b) # not more efficient, oops
    print("efficient mult: ", time.time()-start)
    assert(r1==r2)

#sanityCheck2()


gauss()


'''
# Solve equation Ax=b for an upper triangular matrix A
x = [0 for i in range(n)]
for i in range(n-1, -1, -1):
    x[i] = A[i][n]/A[i][i]
    for k in range(i-1, -1, -1):
        A[k][n] -= A[k][i] * x[i]
return x
'''
