import socket
from decoder.frame import packets_decoder
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.utils import PcapWriter


def read_live_data():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    pcap_writer = PcapWriter("out\\output.pcap", append=True, sync=True)

    while True:
        data, addr = sock.recvfrom(1248)  # buffer size is 1024 bytes
        packet = (
            Ether()
            / IP(dst=UDP_IP, src=addr[0])
            / UDP(dport=UDP_PORT, sport=addr[1])
            / data
        )
        pcap_writer.write(packet)
        yield data


if __name__ == "__main__":
    # ip = sys.argv[1]  # The localhost IP, not the LiDAR's IP.
    # port = int(sys.argv[2])  # 2368 by default
    # for Data in read_live_data(ip, port):
    #     if Data != None:
    #         print(Data)

    live_reader = read_live_data()
    frame_num = 0
    for frame, position in packets_decoder(live_reader):
        if frame:
            frame_num += 1
            print("frame: ", frame_num)
