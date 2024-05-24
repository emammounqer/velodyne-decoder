import struct
from decoder.const import GRANULARITY_MM
from typing import NamedTuple


class Point(NamedTuple):
    laser_id: int
    distance: int
    reflectivity: int


class DataBlock(NamedTuple):
    id: int
    azimuth: int
    data_points: list[Point]


packet_order_laser_id_map: dict[int, int] = {
    1: 31,
    2: 13,
    3: 1,
    4: 17,
    5: 29,
    6: 9,
    7: 3,
    8: 21,
    9: 27,
    10: 12,
    11: 5,
    12: 16,
    13: 25,
    14: 8,
    15: 7,
    16: 20,
    17: 22,
    18: 2,
    19: 10,
    20: 28,
    21: 23,
    22: 6,
    23: 11,
    24: 24,
    25: 18,
    26: 0,
    27: 14,
    28: 30,
    29: 19,
    30: 4,
    31: 15,
    32: 26,
}


def parse_data_block(data_block: bytes, id: int = -1) -> DataBlock:
    """
    angle in hundredths of a degree

    returns: azimuth, data_points (laser_id, distance, reflectivity)
    """
    if len(data_block) != 100:
        raise ValueError("Data block must be exactly 100 bytes.")

    if data_block[0:2] != b"\xff\xee":
        raise ValueError("Invalid flag, expected 0xFFEE.")

    azimuth = decode_azimuth(data_block)
    data_points = parse_data_points(data_block)
    data = DataBlock(id, azimuth, data_points)
    return data


def decode_azimuth(data_block: bytes) -> int:
    azimuth = struct.unpack_from("< H", data_block, 2)[0]
    return azimuth


def parse_data_points(packet_data: bytes) -> list[Point]:
    """
    Parse the data points from the packet data

    Args:
        packet_data: bytes: The packet data

    Returns:
        list[tuple[int, int, int]]: The data points (laser_id, distance, reflectivity)
    """
    data_points: list[Point] = []
    order_in_packet = 0
    for i in range(4, 100, 3):
        distance_uncalibrated_mm, reflectivity = struct.unpack_from("< H B", packet_data, i)
        point = Point(
            packet_order_laser_id_map[order_in_packet],
            distance_uncalibrated_mm * GRANULARITY_MM,
            reflectivity,
        )
        data_points.append(point)
        order_in_packet += 1

    return data_points
