import socket

ip = "127.0.0.1"
port = 5005
message = "hello world"

print "sending packet"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(message, (ip, port))
print "sent"
