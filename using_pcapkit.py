import struct
from typing import Generator
from pcapkit import extract, Ethernet
from decoder.packet_data import decode_factory, decode_time_stamp
from decoder.frame import packets_decoder, frame_to_csv
import time


def parse_payload(payload: Ethernet):
    (return_mode, factory_model) = decode_factory(payload.data)
    print(return_mode, factory_model)


def parse_position_packet(payload: Ethernet):
    offset = 0x00F0
    size = 4
    timestamp_bytes = payload.data[offset : offset + size]
    time = struct.unpack("<I", timestamp_bytes)[0]


def get_packet_generator() -> Generator[bytes, None, None]:
    with extract(
        "data\\VLP-32c_Single.pcap", store=False, nofile=True, auto=False, format="json"
    ) as packets:
        for packet in packets:
            yield packet.payload.data


if __name__ == "__main__":
    packets = get_packet_generator()
    start_time = time.time()
    decoded_packets = packets_decoder(packets)

    frame_num = 0
    position_num = 0
    for frame, position in decoded_packets:
        if frame:
            frame_num += 1
            frame_to_csv(frame)
            print("frame: ", frame_num)
            break
        elif position:
            position_num += 1

    print("frame_num: ", frame_num)
    print("time: ", time.time() - start_time)
