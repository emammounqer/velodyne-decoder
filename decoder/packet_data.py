import struct
from typing import NamedTuple
from decoder.data_block import parse_data_block, DataBlock
from decoder.const import DATA_BLOCK_OFFSET, DATA_BLOCK_SIZE


class PacketData(NamedTuple):
    data_blocks: list[DataBlock]
    time_stamp: int
    return_mode: int
    """
    return_mode:
        Strongest 0x37 (55) \n
        Last Return 0x38 (56) \n
        Dual Return 0x39 (57) \n
    """

    factory_model: int
    """
    factory_model:
        HDL-32E 0x21 (33) \n
        VLP-16 0x22 (34) \n
        Puck LITE 0x22 (34) \n
        Puck Hi-Res 0x24 (36) \n
        VLP-32C 0x28 (40) \n
        Velarray 0x31 (49) \n
        VLS-128 0xA1 (161) \n
    """


def packet_to_csv(packet_data: bytes):
    data_blocks = parse_packet_data_blocks(packet_data, -1, -1, -1)
    csv = "data_block_index, azimuth, laser_id ,distance, reflectivity\n"
    for data_block in data_blocks:
        for data_point in data_block.data_points:
            csv += f"{data_block.block_index, data_block.azimuth, data_point.laser_id, data_point.distance, data_point.reflectivity}\n"

    with open("out/data.csv", "w") as f:
        f.write(csv)


def decode_factory(packet_data: bytes) -> tuple[int, int]:
    return_mode, factory_model = struct.unpack_from("< b b", packet_data, -2)
    return return_mode, factory_model


def decode_time_stamp(packet_data: bytes) -> int:
    timestamp_not_exact = struct.unpack_from("< I", packet_data, -6)[0]
    return timestamp_not_exact


def parse_packet_data_blocks(
    packet_data: bytes, time_stamp: int, return_mode: int, factory_model: int
) -> list[DataBlock]:
    data_blocks: list[DataBlock] = []
    data_block_index = 0

    for _ in DATA_BLOCK_OFFSET:
        data_blocks.append(
            parse_data_block(packet_data, data_block_index, time_stamp, return_mode, factory_model)
        )
        data_block_index += 1

    return data_blocks


def parse_packet_data(packet_data: bytes) -> PacketData:
    time_stamp = decode_time_stamp(packet_data)
    return_mode, factory_model = decode_factory(packet_data)
    data_blocks = parse_packet_data_blocks(packet_data, time_stamp, return_mode, factory_model)

    return PacketData(data_blocks, time_stamp, return_mode, factory_model)
