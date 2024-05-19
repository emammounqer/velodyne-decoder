import struct

def decode_factory(packet_data : bytes):
    return_mode, factory_model = struct.unpack('< b b', packet_data[-2:])
    print(return_mode, factory_model)
    return return_mode, factory_model

def decode_position(packet_data : bytes):
    offset = 0x00f0
    size = 4
    timestamp_bytes = packet_data[offset:offset + size]
    time = struct.unpack('<I', timestamp_bytes)[0]
    print(time)

def decode_time_stamp(packet_data : bytes) -> int:
    timestamp_not_exact :int = struct.unpack('< I', packet_data[-6:-2])[0]
    print(timestamp_not_exact)
    return timestamp_not_exact