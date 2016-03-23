import random
import algorithms
import encoding, decoding
from math import log

def gen_messages(num, length):
    'This method generates random data to act as a message'

    msgs = []
    for i in range(0, num):
        data = gen_data(i, length)
        msgs.append(data)

    return msgs

def format_msg(nodes, msg):
    'Formats the data into a message with a header'

    assert (len(nodes) > 0)

    header = []
    header.append(len(nodes))
    header.extend(nodes)
    result = bytearray(header)
    result.extend(msg)

    return result
    

def gen_data(seed, length):
    'Generates random data in bytes of the specified length'

    rand = random.Random()
    rand.seed(seed)

    data = []
    for i in range(0, length):
        byte = rand.getrandbits(8)
        data.append(byte)

    return bytearray(data)

def get_data(msg):
    num = msg[0]
    return msg[num + 1:]

def get_nodes(msg):
    num = msg[0]
    return list(map(int, msg[1:num + 1]))

'This is passed a row from the processed matrix to generate that message'
def combine_row(row, msgs):
    nodes = []

    for i in range(len(row)):
        # for now, nothings are ignored
        if row[i] != algorithms.DONT_CARE:
            if row[i] > 0:
                nodes.append(i)
    
    if (len(nodes) > 0):
        return combine(nodes, msgs)
    else:
        return None

def combine(nodes, msgs):
    if (len(nodes) == 1):
        return format_msg(nodes, msgs[nodes[0]])

    max_size = max(len(msgs[n]) for n in nodes)
    marker = bytearray([1])
    result = 0
    
    for n in nodes:
        d = msgs[n]
        result += int.from_bytes(marker + d, byteorder='big', signed=False)
        
    return format_msg(nodes, result.to_bytes(max_size + 1, byteorder='big'))

# This needs to be updated for new encoding
def extract(node, msg, side_info):
    nodes = get_nodes(msg)
    
    # make sure this is possible
    assert node in nodes
    
    data = get_data(msg)
    data_int = int.from_bytes(data, byteorder='big', signed=False)
    marker = bytearray([1])

    for n in nodes:
        # check to see if this is our target
        if n == node:
            continue

        side = side_info[n]
        # make sure we have the side info
        if side == None or len(side) == 0:
            return None

        # subtract the side info
        data_int -= int.from_bytes(marker + side, byteorder='big', signed=False)
    
    assert(data_int != 0)
    length = int(log(data_int, 256)) + 1
    return data_int.to_bytes(length, byteorder='big')[1:]

    
        

        
    
        

