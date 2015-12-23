import udp
import socket
import threading

ACK_PORT = 5005
ACK_TIMEOUT = 1
ACK_BUFFER = 256

class AckListener:
    'Handles ack messages and tracking'

    def __init__(self, numNodes):
        self.acks = [[0 for x in range(numNodes)] for x in range(numNodes)]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", ACK_PORT))
        self.sock.settimeout(ACK_TIMEOUT)
        self.timeouts = 0
        self.run = False

    'This is intended to be run as a thread see the start method'
    def listen(self):
        while (self.run):
            ack = None 
            try:
                ack = self.sock.recvfrom(ACK_BUFFER)
                print "Got ack:", ack
                
                # break of the message into it's info
                broken = ack[0].split()
                node = int (broken[0])
                msgId = int (broken[1])
                
                # record the ack
                self.acks[node][msgId] = 1

            # Timeouts will happen, we dont need to do anything
            except socket.timeout:
                self.timeouts += 1

    def start(self):
        self.run = True
        self.stopped = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        self.run = False
        self.thread.join()

class AckSender:
    'Handles the sending of acks so we can have a standard format'

    def __init__(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip

    def ack(self, myId, messageId):
        print "sending ack for", myId, messageId
        msg = "{0} {1}".format(myId, messageId)
        self.sock.sendto(msg, (self.ip, ACK_PORT))

