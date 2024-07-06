from typing import Generator
from pcapkit import extract, Ethernet
from decoder.frame import packets_decoder, frame_to_csv, get_frames
from processing.background_filter import background_filter
import time


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
    background_filter(get_frames(decoded_packets))

    # frame_num = 0
    # position_num = 0
    # for frame, position in decoded_packets:
    #     if frame:
    #         if frame_num == 0:
    #             frame_num += 1
    #             continue
    #         # frame_to_csv(frame)

    #         print("frame: ", frame_num)
    #         frame_num += 1
    #     elif position:
    #         position_num += 1

    # print("frame_num: ", frame_num)
    print("time: ", time.time() - start_time)
