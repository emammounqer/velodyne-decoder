import struct


def decode_factory(packet_data: bytes):
    return_mode, factory_model = struct.unpack("< b b", packet_data[-2:])
    return return_mode, factory_model


def decode_time_stamp(packet_data: bytes) -> int:
    timestamp_not_exact: int = struct.unpack("< I", packet_data[-6:-2])[0]
    return timestamp_not_exact


def decode_exact_time_stamp(packet_data: bytes):
    pass
