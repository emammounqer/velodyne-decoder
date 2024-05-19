import struct
from pcapkit import extract, Frame, Ethernet
from time_stamp import get_time_stamp

    
def parse_payload(payload : Ethernet):
    try:
        timestamp_not_exact, return_mode, factory_model = struct.unpack('< I b b', payload.data[-6:])
        print(timestamp_not_exact, return_mode, factory_model)
    except Exception as e:
        print(e)
        # throw exception
        raise

def parse_position_packet(payload : Ethernet):
    offset = 0x00f0
    size = 4
    timestamp_bytes = payload.data[offset:offset + size]
    time = struct.unpack('<I', timestamp_bytes)[0]
    print(time)
        
    
packets_num = 0
with extract('data\\t1.pcap',store=False, nofile=True,auto=False,format='json') as packets:
    for packet in packets:
        if len(packet.payload) == 1248:
            pass
            # parse_payload(packet.payload)
        elif len(packet.payload) == 554:
            parse_position_packet(packet.payload)
        packets_num += 1
