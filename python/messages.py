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


def gen_data(seed, length):
    'Generates random data in bytes of the specified length'

    rand = random.Random()
    rand.seed(seed)

    data = []
    for i in range(0, length):
        byte = rand.getrandbits(8)
        data.append(byte)

    return bytearray(data)


def get_test(msg):
    return msg[0]


def get_data(msg, coeff_size=50):
    num = msg[1]
    return msg[2 + num + (num * coeff_size):]


def get_coeffs(msg, num_nodes, coeff_size=50):
    num = msg[1]
    coeffs = [0] * num_nodes
    
    for i in range(num):
        id_index = 2 + i + (i * coeff_size)
        coeff_index = id_index + 1
        coeff_index_end = coeff_index + coeff_size

        msg_id = msg[id_index]
        coeff = int.from_bytes(msg[coeff_index : coeff_index_end], byteorder='big', signed=True)
        coeffs[msg_id] = coeff
        
    return coeffs


'This is passed a row from the processed matrix to generate that message'
def encode_row(row, msgs, tid, coeff_size=50):
    header = [tid, 0]
    msg = encoding.EncodedMessage(0, rawEncoding=True)
    mod_factor = ((2**(coeff_size * 8)) / 2) - 1;

    for i in range(len(row)):    
        # for now, nothings are ignored
        if row[i] != 0 and row[i] != algorithms.DONT_CARE:
            header[1] += 1
            header.append(i)
            
            if row[i] >= mod_factor:
                row[i] = row[i] % mod_factor
                print("WARNING: We went outside of our encoding range. messanges.py:encode_row)")

            header.extend(row[i].to_bytes(coeff_size, byteorder='big', signed=True))
            msg = msg + (encoding.EncodedMessage(msgs[i]) * row[i])
    
    if header[1] > 0:
        header = bytearray(header)
        return header + msg.toBytes(removeMarker=False)
    else:
        return None       

