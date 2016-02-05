import random

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

    random.seed(seed)

    data = []
    for i in range(0, length):
        byte = random.getrandbits(8)
        data.append(byte)

    return bytearray(data)

def get_data(msg):
    num = msg[0]
    return msg[num + 1:]

def get_nodes(msg):
    num = msg[0]
    return list(map(int, msg[1:num + 1]))

def combine(nodes, msgs):
    max_size = max(len(msgs[n]) for n in nodes)
    marker = bytearray([1])
    result = long(0)
    
    for n in nodes:
        d = data[n]
        result += int.from_bytes(marker + d, byteorder='big', signed=False)
        
    return format_msg(nodes, int.to_bytes(max_size + 1, byteorder='big'))

#def extract(node, msg, side_info):
     #nodes = get_nodes(msg)
     #data = (bytearray) get_data(msg)

     


    
    



