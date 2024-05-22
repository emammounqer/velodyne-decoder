import struct
from decoder.data_block import parse_data_block
from decoder.const import DATA_BLOCK_OFFSET, DATA_BLOCK_SIZE


def packet_to_csv(packet_data: bytes):
    data_blocks = parse_packet_data_blocks(packet_data)
    csv = "data_block_index, azimuth, laser_id ,distance, reflectivity\n"
    for data_block in data_blocks:
        for data_point in data_block[1][1]:
            csv += (
                f"{data_block[0], data_blocks[1][0], data_point[0], data_point[1], data_point[2]}\n"
            )

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
):
    """
    Parse the data blocks from the packet data.

    Returns:
        data_blocks[i][0] = data_block_index
        data_blocks[i][1] = data block
        data_blocks[i][1][0] = azimuth
        data_blocks[i][1][1] = data points
        data_blocks[i][1][1][0] = laser_id
        data_blocks[i][1][1][1] = distance
        data_blocks[i][1][1][2] = reflectivity

    """
    data_blocks: list[tuple[int, tuple[int, list[tuple[int, int, int]]]]] = []
    data_block_index = 0

    for data_block_offset in DATA_BLOCK_OFFSET:
        data_block = packet_data[data_block_offset : data_block_offset + DATA_BLOCK_SIZE]
        data_blocks.append((data_block_index, parse_data_block(data_block)))
        data_block_index += 1

    return data_blocks
