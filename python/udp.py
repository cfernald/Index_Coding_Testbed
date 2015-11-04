import sys
from socket import *

class UdpBroadcaster:
  'Sends broadcast messages to network'
  addr = ''
  
  def __init__(self, addr):
    self.soc = socket(AF_INET, SOCK_DGRAM)
    self.soc.bind((self.addr, 0))
    self.soc.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

  def send(self, message, port):
    self.soc.sendto(message, ('<broadcast>', port))

'''class UdpReceiver:
  'Receives UDP packets on the network'

  def __init__(self, addr, port):
  '''
