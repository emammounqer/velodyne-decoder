import os
from decoder.const import PACKET_SIZE, POSITION_PACKET_SIZE
from decoder.packet_data import parse_packet_data, PacketData
from decoder.position_packet import parse_position_packet
from typing import Generator, Iterable, Any, NamedTuple


class Frame(NamedTuple):
    id: int
    data: list[PacketData]


def accumulate_frames(data_packets):
    frame = []
    previous_azimuth = -1

    for packet in data_packets:
        data_blocks = parse_packet_data(packet)

        if previous_azimuth != -1 and data_blocks.data_blocks[1][0] < previous_azimuth:
            # Azimuth wrapped around, indicating a new frame
            yield frame
            frame = []

        frame.extend(data_blocks)
        previous_azimuth = data_blocks.data_blocks[1][0]

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
            data_blocks = parse_packet_data(data_packet)
            curr_azimuth = data_blocks.data_blocks[0].azimuth
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


def frame_to_csv(frame: Frame):
    csv = "data_block_index,block_azimuth, point_azimuth, laser_id ,distance, reflectivity, time_stamp, vertical_angle,x ,y ,z\n"
    for packet in frame.data:
        for data_block in packet.data_blocks:
            for data_point in data_block.data_points:
                csv += f"{data_block.block_index,data_block.azimuth, data_point.azimuth, data_point.laser_id, data_point.distance, data_point.reflectivity, data_point.timestamp, data_point.vertical_angle, data_point.x, data_point.y, data_point.z}\n"

    if not os.path.exists("out/frames"):
        os.makedirs("out/frames")

    with open(f"out/frames/data{frame.id}.csv", "w") as f:
        f.write(csv)


def packets_decoder(
    b_packets: Iterable[bytes],
) -> Generator[tuple[Frame | None, Any], None, None]:
    frame_packets: list[PacketData] = []
    curr_frame_num: int = 0
    previous_azimuth: int = -1
    curr_azimuth: int = -1

    for b_packet in b_packets:
        if len(b_packet) == PACKET_SIZE:
            packet_data: PacketData = parse_packet_data(b_packet)
            if previous_azimuth == -1:
                previous_azimuth = packet_data.data_blocks[0].azimuth

            last_azimuth = packet_data.data_blocks[-1].azimuth
            # check if the complete rotation
            if last_azimuth < previous_azimuth:
                # check where the azimuth wraps around
                for i in range(len(packet_data.data_blocks)):
                    curr_azimuth = packet_data.data_blocks[i].azimuth

                    if curr_azimuth < previous_azimuth:
                        curr_packet_data: PacketData = PacketData(
                            packet_data.data_blocks[:i],
                            packet_data.time_stamp,
                            packet_data.return_mode,
                            packet_data.factory_model,
                        )
                        frame_packets.append(curr_packet_data)
                        yield (Frame(curr_frame_num, frame_packets), None)
                        curr_frame_num += 1

                        next_packet_data: PacketData = PacketData(
                            packet_data.data_blocks[i:],
                            packet_data.time_stamp,
                            packet_data.return_mode,
                            packet_data.factory_model,
                        )
                        frame_packets = [next_packet_data]
                        break

                    previous_azimuth = curr_azimuth

            else:
                frame_packets.append(packet_data)

            previous_azimuth = last_azimuth

        elif len(b_packet) == POSITION_PACKET_SIZE:
            yield (None, parse_position_packet(b_packet))


def get_frames(
    packets: Generator[tuple[Frame | None, Any], None, None]
) -> Generator[Frame, None, None]:
    for frame, position in packets:
        if frame:
            yield frame
        elif position:
            continue
