import struct
from typing import Generator
from pcapkit import extract, Frame, Ethernet
from decoder.time_stamp import get_time_stamp
from decoder.packet_data import decode_factory, decode_time_stamp
from decoder.frame import packet_decoder, frame_to_csv
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
    with extract("data\\t1.pcap", store=False, nofile=True, auto=False, format="json") as packets:
        for packet in packets:
            yield packet.payload.data


# start_time = time.time()
# packets_num = 0
# frames_num = 0
# with extract("data\\t1.pcap", store=False, nofile=True, auto=False, format="json") as packets:
#     frames = frame_generator()
#     next(frames)
#     for packet in packets:
#         if len(packet.payload) == 1248:
#             frame = frames.send(packet.payload.data)
#             if frame:
#                 next(frames)
#                 frame_to_csv(frame, frames_num)
#                 frames_num += 1
#         elif len(packet.payload) == 554:
#             parse_position_packet(packet.payload)
#         packets_num += 1

# print("Packets: ", packets_num)
# print("Frames: ", frames_num)
# print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    packets = get_packet_generator()
    decoded_packets = packet_decoder(packets)

    frame_num = 0
    position_num = 0
    for frame, position in decoded_packets:
        if frame:
            frame_num += 1
            print("frame: ", frame_num)
        elif position:
            position_num += 1
            print("position: ", position_num)
