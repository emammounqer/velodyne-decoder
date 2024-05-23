import struct
from typing import NamedTuple
from decoder.data_block import parse_data_block, DataBlock
from decoder.const import DATA_BLOCK_OFFSET, DATA_BLOCK_SIZE


def packet_to_csv(packet_data: bytes):
    data_blocks = parse_packet_data_blocks(packet_data)
    csv = "data_block_index, azimuth, laser_id ,distance, reflectivity\n"
    for data_block in data_blocks:
        for data_point in data_block.data_points:
            csv += f"{data_block.id, data_block.azimuth, data_point.laser_id, data_point.distance, data_point.reflectivity}\n"

    with open("out/data.csv", "w") as f:
        f.write(csv)


def decode_factory(packet_data: bytes):
    return_mode, factory_model = struct.unpack_from("< b b", packet_data, -2)
    return return_mode, factory_model


def decode_time_stamp(packet_data: bytes) -> int:
    timestamp_not_exact = struct.unpack_from("< I", packet_data, -6)[0]
    return timestamp_not_exact


def decode_exact_time_stamp(packet_data: bytes):
    pass


def parse_packet_data_blocks(
    packet_data: bytes,
) -> list[DataBlock]:
    """
    Parse the data blocks from the packet data.

    Returns:
        list[DataBlock]

    """
    data_blocks: list[DataBlock] = []
    data_block_index = 0

    for data_block_offset in DATA_BLOCK_OFFSET:
        data_block = packet_data[data_block_offset : data_block_offset + DATA_BLOCK_SIZE]
        data_blocks.append(parse_data_block(data_block, data_block_index))
        data_block_index += 1

    return data_blocks
