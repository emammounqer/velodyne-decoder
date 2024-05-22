import struct


def decode_position(packet_data: bytes):
    offset = 0x00F0
    size = 4
    timestamp_bytes = packet_data[offset : offset + size]
    time = struct.unpack("<I", timestamp_bytes)[0]
    return time


def parse_position_packet(packet_data: bytes):
    return decode_position(packet_data)
