import dpkt
import socket

def read_pcap_in_chunks(file_path, chunk_size=1024):
    with open(file_path, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        
        buffer = bytearray()
        for timestamp, buf in pcap:
            buffer.extend(buf)
            while len(buffer) >= chunk_size:
                process_chunk(buffer[:chunk_size])
                buffer = buffer[chunk_size:]
                
        # Process any remaining bytes in the buffer
        if buffer:
            process_chunk(buffer)

def process_chunk(chunk):
    try:
        eth = dpkt.ethernet.Ethernet(chunk)
        if isinstance(eth.data, dpkt.ip.IP):
            ip = eth.data
            if isinstance(ip.data, dpkt.udp.UDP):
                udp = ip.data
                src_ip = socket.inet_ntoa(ip.src)
                dst_ip = socket.inet_ntoa(ip.dst)
                src_port = udp.sport
                dst_port = udp.dport
                udp_data = udp.data

                print("\n ----------------- \n")
                print(f'UDP Packet: {src_ip}:{src_port} -> {dst_ip}:{dst_port} ')
                print("\n ----------------- \n")
                print(f'UDP Data: {udp_data}')
                exit()
                
    except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
        pass  # Incomplete or corrupted packet

if __name__ == "__main__":
    file_path = 'data\\VLP-32c_Single.pcap'
    read_pcap_in_chunks(file_path)