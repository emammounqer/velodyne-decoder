import socket
from using_pcapkit import get_packet_generator

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP

for i, packet in enumerate(list(get_packet_generator())):
    sock.sendto(packet, (UDP_IP, UDP_PORT))
    print(f"Sent packet {i}")
