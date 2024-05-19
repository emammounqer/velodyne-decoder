import struct

DATA_BLOCK_SIZE = 100
DATA_BLOCK_COUNT = 12
DATA_BLOCK_OFFSET = 42
DATA_BLOCK_INDEXES = [42, 142, 242, 342, 442, 542, 642, 742, 842, 942, 1042, 1142]
GRANULARITY_MM = 4


# TODO: remove this function
def parse_packet_data_blocks(packet_data: bytes):
    data_blocks = []
    for i in DATA_BLOCK_INDEXES:
        data_block = packet_data[i : i + DATA_BLOCK_SIZE]
        data_blocks.append(parse_data_block(data_block))
    return data_blocks


def decode_azimuth(data_block: bytes) -> int:
    azimuth = struct.unpack("< H", data_block[2:4])[0]
    return azimuth


def parse_data_block(data_block: bytes):
    """
    angle in hundredths of a degree
    """
    if len(data_block) != 100:
        raise ValueError("Data block must be exactly 100 bytes.")

    if data_block[0:2] != b"\xff\xee":
        raise ValueError("Invalid flag, expected 0xFFEE.")

    azimuth = decode_azimuth(data_block)

    # TODO:  azimuth should be between 0 to 35999
    return azimuth


def parse_data_points(packet_data: bytes) -> list[tuple[int, int]]:
    #  distance and one byte of calibrated reflectivity
    data_points: list[tuple[int, int]] = []
    for i in range(4, 100, 3):
        data_point = packet_data[i : i + 3]
        distance_uncalibrated_mm, reflectivity = struct.unpack("< H B", data_point)
        data_points.append((distance_uncalibrated_mm * GRANULARITY_MM, reflectivity))

    return data_points
