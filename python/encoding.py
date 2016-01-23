import random
import time

class AppendEncoding:
	def __init__(self, message, rawEncoding=False):
		if rawEncoding:
			self.encoding = message
		else:
			self.encoding = self.encode(message)
	
	def __add__(self, other):
	    return AppendEncoding(self.encoding + other.encoding, rawEncoding=True)

	def __sub__(self, other):
		return AppendEncoding(self.encoding - other.encoding, rawEncoding=True)

	def __mul__(self, other):
        return AppendEncoding(self.encoding * other.encoding, rawEncoding=True) # indent?
	
	def __eq__(self, other):
		return self.encoding == other.encoding

	def __repr__(self):
		return self.decode(self.encoding)
	
	def getEncoding(self):
		return self.encoding

	def encode(self, m):
		#start with a 1 to protect against opening characters less than 100 (like 06) have their opening 0s chopped off in long representation
		numberified = ["1"]
		for c in str(m):
			n = ord(c) #31 is the lowest meaningful ascii-- that of a space. Now the highest meaningful ascii can be represented in 2 chars (126-31)
			if n<10:
				numberified.append("00"+str(n))
			elif n<100:
				numberified.append("0"+str(n))
			else:
				numberified.append(str(n))
		return  long("".join(numberified))

	def decode(self, m):
		message = []
		threeMod = 0
		charBuffer = []
		for c in str(m)[1:]: #skip the opening '1' which is just there for messages with a first shifted character less than 10
			charBuffer.append(c)
			threeMod += 1
			if(threeMod % 3 == 0):
				message.append( chr( int("".join(charBuffer))) )
				del charBuffer[:]
		return "".join(message)

'''
messageLength = 100
message1 = []
message2 = []
message3 = []
for i in range(messageLength):
	message1.append( chr(random.randint(0,255)) )
	message2.append( chr(random.randint(0,255)) )
	message3.append( chr(random.randint(0,255)) )	

message1 = "".join(message1)
message2 = "".join(message2)
message3 = "".join(message3)

encodeStart = time.time()
message1 = AppendEncoding(message1)
message2 = AppendEncoding(message2)
message3 = AppendEncoding(message3)
encodeEnd = time.time()

addStart = time.time()
comb = message1+message2+message3
addEnd = time.time()

decodeStart = time.time()
#use str() on each to force __repr__() to be called, thus actually decoding
print str(message3)==str((comb - (message1+message2)))
decodeEnd = time.time()

print("\n{0} to encode; {1} to decode".format(encodeEnd-encodeStart, decodeEnd-decodeStart))

# print comb - (message1+message2)
'''