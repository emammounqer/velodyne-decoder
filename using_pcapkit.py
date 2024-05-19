import struct
from pcapkit import extract, Frame, Ethernet
from decoder.time_stamp import get_time_stamp
from decoder.decoder import decode_factory, decode_time_stamp


def parse_payload(payload: Ethernet):
    (return_mode, factory_model) = decode_factory(payload.data)
    print(return_mode, factory_model)


def parse_position_packet(payload: Ethernet):
    offset = 0x00F0
    size = 4
    timestamp_bytes = payload.data[offset : offset + size]
    time = struct.unpack("<I", timestamp_bytes)[0]
    print(time)


packets_num = 0
with extract(
    "data\\t1.pcap", store=False, nofile=True, auto=False, format="json"
) as packets:
    for packet in packets:
        if len(packet.payload) == 1248:
            parse_payload(packet.payload)
        elif len(packet.payload) == 554:
            parse_position_packet(packet.payload)
        packets_num += 1
