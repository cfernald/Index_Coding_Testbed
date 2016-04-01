import decoding, encoding

class DecodeManager:
    'Handles the state info for decoding and runs decoding'

    def __init__(self, numNodes): 
        self.numNodes = numNodes
        self.reset()


    def reset(self):
        self.coeffs = []
        self.decoding_steps = []
        self.side_info = {}
        self.encoded = []

    def direct_decode(self, coeffs, steps):
        # decode what we can first
        for msgId in range(len(coeffs)):
            if (coeffs[msgId] != 0):
                if msgId in self.side_info:
                        
                    # We already have this msgId decoded, lets extract it
                    num_msgId = coeffs[msgId]
                    div = self.side_info[msgId][1]
                    steps_msgId = self.side_info[msgId][0]
                        
                    # update the orig_msg matrix
                    for i in range(len(coeffs)):
                        coeffs[i] *= div
                        coeffs[msgId] = 0
                        
                    # update the steps list
                    for i in range(len(steps_msgId)):
                        steps[i] = (steps[i] * div) - (num_msgId * steps_msgId[i])

        return coeffs, steps


    def find_new_decoded(self):
        rows_to_be_removed = []
        new_decoded = []

        for i in range(len(self.coeffs)):
            canDecode = False
            div = 0
            msgId = -1
        
            # see if this row is decodable (only one coeff)
            for j, colVal in enumerate(self.coeffs[i]):
                if canDecode and colVal != 0:
                    canDecode = False
                    break
                if not canDecode and colVal != 0:
                    canDecode = True
                    div = colVal
                    msgId = j
        
            if canDecode:
                rows_to_be_removed.append(i)
                self.side_info[msgId] = (self.decoding_steps[i], div)

        rows_to_be_removed.reverse()
        for row in rows_to_be_removed:
            self.coeffs.pop(row)
            self.decoding_steps.pop(row)
    
        return new_decoded


    def addMessage(self, nodes, data):
        # Nodes is the coeffs array for this message
        # Data is the actually encoded data from the message
        new_decoded = []

        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1
           
        # update th active steps
        for i in range(len(self.decoding_steps)):
            self.decoding_steps[i].append(0)

        # create our steps list
        steps = ([0] * len(self.encoded)) + [1]

        if num_coeffs > 1: # do quick decoding for side_info stuff
            # decode what we can first
            self.direct_decode(nodes, steps) 
       
        # Check the coeffs again to see if it need to be added to the matrix
        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1

        if num_coeffs > 1:    
            # Add new coeffs row
            self.coeffs.append(nodes)

            # add the new decing steps and raw_msg
            self.decoding_steps.append(steps)

            # Add a call to gauss and return a list of new decoded
            self.coeffs, self.decoding_steps = decoding.gauss(self.coeffs, self.decoding_steps)
        
        else:
            # This is a single message encoding
            for i in range(len(nodes)):
                if (nodes[i] != 0):
                    # add the elimination steps array as well as the coefficient of our single message data to be divided by at decode time
                    if i not in self.side_info:
                        self.side_info[i] = (steps, nodes[i])
                        new_decoded.append(i)
                        
                        for row in range(len(self.coeffs)):
                            self.direct_decode(self.coeffs[row], self.decoding_steps[row])
                        
            
        # Find if there is anything new for us to decode 
        new_decoded.extend(self.find_new_decoded())
        # store the original encoded combination
        self.encoded.append(data)

        return new_decoded

def test():
    dh = DecodeManager(3)
    l = dh.addMessage([1,0,0],b"dfsdf")
    assert l == [0]
    l = dh.addMessage([1,1,0],b"sadf")
    assert l == [1]
    l = dh.addMessage([1,1,1],b"asdf")
    assert l == [2]
    assert len(dh.coeffs) == 0
    assert len(dh.side_info) == 3
    assert len(dh.decoding_steps) == 0
    
    dh.reset()
    l = dh.addMessage([1,1,1],b"asdf")
    assert l == []
    l = dh.addMessage([1,1,1],b"sadf")
    assert l == []
    assert len(dh.coeffs) == 2
    assert len(dh.side_info) == 0
    assert len(dh.decoding_steps) == 2

    dh.reset()
    l = dh.addMessage([1,0,1], b"sdf")
    assert l == []
    l = dh.addMessage([0,1,1], b"sdaf")
    assert l == []
    l = dh.addMessage([1,1,0], b"asdf")
    print(sorted(l))
    assert sorted(l) == [0,1,2]

    print("Test passed")

