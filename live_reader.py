import socket
from decoder.frame import packets_decoder, frame_to_csv, get_frames
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.utils import PcapWriter
from processing.background_filter import background_filter
import threading
import queue


def write_pcap(pcap_writer, packet_queue):
    while True:
        packet = packet_queue.get()
        if packet is None:
            break
        pcap_writer.write(packet)

def data_generator(data_queue):
    while True:
        data = data_queue.get()
        if data is None:
            break
        yield data

def process_frames(data_queue):
    frame_num = 0
    data_gen = data_generator(data_queue)
    decoder = packets_decoder(data_gen)
    for frame, position in decoder:
        if frame:
            frame_to_csv(frame)
            frame_num += 1
            print("frame: ", frame_num)

def read_live_data():
    UDP_IP = "192.168.1.222"
    UDP_PORT = 2368
    BUFFER_SIZE = 65536 * 3
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.bind((UDP_IP, UDP_PORT))
    
    pcap_writer = PcapWriter("out\\output.pcap", append=True, sync=True)
    packet_queue = queue.Queue()
    data_queue = queue.Queue()
    
    # Start the PCAP writing thread
    write_thread = threading.Thread(target=write_pcap, args=(pcap_writer, packet_queue))
    write_thread.start()
    
    # Start the frame processing thread
    process_thread = threading.Thread(target=process_frames, args=(data_queue,))
    process_thread.start()
    
    try:
        while True:
            data, addr = sock.recvfrom(1248)  # buffer size is 1024 bytes
            packet = (
                Ether()
                / IP(dst=UDP_IP, src=addr[0])
                / UDP(dport=UDP_PORT, sport=addr[1])
                / data
            )
            packet_queue.put(packet)
            data_queue.put(data)
    except KeyboardInterrupt:
        # Signal the threads to stop
        packet_queue.put(None)
        data_queue.put(None)
        # Wait for the threads to finish
        write_thread.join()
        process_thread.join()
    finally:
        sock.close()
        pcap_writer.close()

if __name__ == "__main__":
    read_live_data()