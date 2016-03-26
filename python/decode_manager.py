import decoding, encoding, messages

class DecodeManager:
    'Handles the state info for decoding and runs decoding'

    def __init__(self, numNodes): 
        self.numNodes = numNodes
        self.reset()

    def reset(self):
        self.coeffs = []
        self.decoding_steps = []
        seld.side_info = {}
        self.encoded = []

    def addMessage(self, raw_msg):
        nodes = messages.get_nodes(raw_msg)
        data = messages.get_data(raw_msg)

        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1
           
        # update th active steps
        for i in range(len(self.decoding_steps)):
            self.decoding_steps[i].append(0)

        # create our steps list
        steps = ([0] * len(self.encoded)) + [1]

        if num_coeffs > 1: #TODO do quick decoding for side_info stuff
            #decode what we can first
            for msgId in range(len(nodes)):
                if (nodes[msgId] != 0):
                    if msgId in self.side_info:
                        
                        # We already have this msgId decoded, lets extract it
                        num_msgId = nodes[msgId]
                        div = self.sife_info[msgId][1]
                        steps_msgId = self.side_info[msgId][0]
                        
                        # update the orig_msg matrix
                        for i in range(len(nodes)):
                            nodes[i] *= div
                        nodes[msgId] = 0
                        
                        # update the steps list
                        for i in range(len(steps_msgId)):
                            steps[i] = (steps[i] * mult) - (num_msgId * steps_msgId[i])
       
        # Check the coeffs again to see if it need to be added to the matrix
        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1

        if coeffs > 1:    
            # Add new coeffs row
            self.coeffs.append(nodes)

            # add the new decing steps and raw_msg
            self.decoding_steps.append(steps) 
        
        else:
            # This is a single message encoding
            for i in range(len(nodes)):
                if (nodes[i] != 0):
                    # add the elimination steps array as well as the coefficient of our single message data to be divided by at decode time
                    self.side_info[i] = tuple(steps, nodes[i])
                        
      
        self.encoded.append(raw_msg)
