import udp
import socket
import threading

ACK_PORT = 5005
ACK_TIMEOUT = 0.001
ACK_BUFFER = 256

class AckListener:
    'Handles ack messages and tracking'

    def __init__(self, numNodes):
        self.acks = [[0 for x in range(numNodes)] for x in range(numNodes)]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", ACK_PORT))
        #self.sock.settimeout(ACK_TIMEOUT)
        self.run = False

    def listen(self):
        while (self.run):
            ack = self.sock.recvfrom(ACK_BUFFER)
            print "Got ack:", ack
            # need to come up with a format for the acks

    def start(self):
        self.run = True
        self.stopped = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        self.run = False
        self.thread.join()
