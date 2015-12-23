'This is the file that contains the algorithm codes and determines with algorithm is being used'

def reduceMessages(messages, acks):
    return roundRobin(messages, acks)

def roundRobin(messages, acks):
    'This method just identifies the the missing 1s along the diagnal'
    
    result = []

    for i in range(0, len(messages)):
        if (acks[i][i] == 0):
            result.append(messages[i])

    return result


    
