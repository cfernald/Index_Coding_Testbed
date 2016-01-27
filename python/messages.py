import random

def gen_messages(num, length):
    msgs = []
    for i in range(0, num):
        data = gen_data(i, length)
        msgs.append(data)

    return msgs

def format_msg(nodes, msg):
    assert (len(nodes) > 0)

    header = []
    header.append(len(nodes))
    header.extend(nodes)
    result = bytearray(header)
    result.extend(msg)

    return result
    

def gen_data(seed, length):
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
    return map(int, msg[1:num + 1])

