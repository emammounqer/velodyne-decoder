from decoder.packet_data import parse_packet_data_blocks, PacketData
from decoder.position_packet import parse_position_packet
from typing import Generator, Iterable, Any


type Frame = tuple[int, PacketData]


def accumulate_frames(data_packets):
    frame = []
    previous_azimuth = -1

    for packet in data_packets:
        data_blocks = parse_packet_data_blocks(packet)

        if previous_azimuth != -1 and data_blocks[1][0] < previous_azimuth:
            # Azimuth wrapped around, indicating a new frame
            yield frame
            frame = []

        frame.extend(data_blocks)
        previous_azimuth = data_blocks[1][0]

    if frame:
        yield frame


def frame_generator():
    frame = []
    previous_azimuth = -1
    curr_azimuth = -1
    diff_azimuth = 0

    while True:
        data_packet: bytes = yield

        try:
            if not data_packet:
                continue
            data_blocks = parse_packet_data_blocks(data_packet)
            curr_azimuth = data_blocks[0][1][0]
        except ValueError:
            print("Invalid data packet")
            continue

        if diff_azimuth >= 36000:
            yield frame
            frame = []
            diff_azimuth = 0

        if previous_azimuth > -1 and curr_azimuth < previous_azimuth:
            diff_azimuth += 36000 - previous_azimuth + curr_azimuth
        elif previous_azimuth > -1:
            diff_azimuth += curr_azimuth - previous_azimuth

        frame.extend(data_blocks)
        previous_azimuth = curr_azimuth


def frame_to_csv(frame, frame_index):
    csv = "data_block_index, azimuth, laser_id ,distance, reflectivity\n"
    for data_block in frame:
        for data_point in data_block[1][1]:
            csv += (
                f"{data_block[0], data_block[1][0], data_point[0], data_point[1], data_point[2]}\n"
            )

    with open(f"out/frames/data{frame_index}.csv", "w") as f:
        f.write(csv)


def packets_decoder(packets: Iterable[bytes]) -> Generator[tuple[Frame | None, Any], None, None]:
    frame: PacketData = []
    curr_frame: int = 0
    previous_azimuth: int = -1
    curr_azimuth: int = -1
    diff_azimuth: int = 0

    for packet in packets:
        if len(packet) == 1248:
            data_blocks: PacketData = parse_packet_data_blocks(packet)
            curr_azimuth = data_blocks[0][1][0]

            # Check if the azimuth has wrapped around for next packet
            if previous_azimuth > -1 and curr_azimuth < previous_azimuth:
                diff_azimuth += 36000 - previous_azimuth + curr_azimuth
            elif previous_azimuth > -1:
                diff_azimuth += curr_azimuth - previous_azimuth

            if diff_azimuth >= 36000:
                curr_frame += 1
                yield ((curr_frame, frame), None)
                frame = []
                diff_azimuth = 0

            frame.extend(data_blocks)
            previous_azimuth = curr_azimuth

        elif len(packet) == 554:
            yield (None, parse_position_packet(packet))
