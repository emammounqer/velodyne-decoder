import struct
from decoder.const import (
    GRANULARITY_MM,
    DATA_BLOCK_OFFSET,
    FULL_FIRING_CYCLE_TIME,
    SINGLE_FIRING_TIME,
)
from typing import NamedTuple


class Point(NamedTuple):
    laser_id: int
    distance: int
    reflectivity: int
    timestamp: float
    azimuth: float
    vertical_angle: float


class DataBlock(NamedTuple):
    block_index: int
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

# Laser ID Elevation Angle (°) Azimuth Offset (δ)
laser_data = [
    (0, -25, 1.4),
    (1, -1, -4.2),
    (2, -1.667, 1.4),
    (3, -15.639, -1.4),
    (4, -11.31, 1.4),
    (5, 0, -1.4),
    (6, -0.667, 4.2),
    (7, -8.843, -1.4),
    (8, -7.254, 1.4),
    (9, 0.333, -4.2),
    (10, -0.333, 1.4),
    (11, -6.148, -1.4),
    (12, -5.333, 4.2),
    (13, 1.333, -1.4),
    (14, 0.667, 4.2),
    (15, -4, -1.4),
    (16, -4.667, 1.4),
    (17, 1.667, -4.2),
    (18, 1, 1.4),
    (19, -3.667, -4.2),
    (20, -3.333, 4.2),
    (21, 3.333, -1.4),
    (22, 2.333, 1.4),
    (23, -2.667, -1.4),
    (24, -3, 1.4),
    (25, 7, -1.4),
    (26, 4.667, 1.4),
    (27, -2.333, -4.2),
    (28, -2, 4.2),
    (29, 15, -1.4),
    (30, 10.333, 1.4),
    (31, -1.333, -1.4),
]


def parse_data_block(
    packet_data: bytes, block_index: int, time_stamp: int, return_mode: int, factory_model: int
) -> DataBlock:
    azimuth: int = struct.unpack_from("< H", packet_data, 2 + DATA_BLOCK_OFFSET[block_index])[0]

    data_points = parse_data_points(
        packet_data, block_index, azimuth, time_stamp, return_mode, factory_model
    )
    data = DataBlock(block_index, azimuth, data_points)
    return data


def parse_data_points(
    packet_data: bytes,
    block_index: int,
    azimuth: int,
    time_stamp: int,
    return_mode: int,
    factory_model: int,
) -> list[Point]:
    data_points: list[Point] = []
    order_in_packet = 0
    for i in range(4 + DATA_BLOCK_OFFSET[block_index], 100 + DATA_BLOCK_OFFSET[block_index], 3):
        distance_uncalibrated_mm, reflectivity = struct.unpack_from("< H B", packet_data, i)
        if distance_uncalibrated_mm == 0:
            order_in_packet += 1
            continue

        offset_index = block_index // 2 if return_mode == 0x39 else block_index
        offset = offset_index * FULL_FIRING_CYCLE_TIME + order_in_packet // 2 * SINGLE_FIRING_TIME
        point_time_stamp = offset + time_stamp

        point_azimuth = azimuth + (laser_data[order_in_packet][2] * 100)
        if point_azimuth >= 36000:
            point_azimuth -= 36000
        if point_azimuth < 0:
            point_azimuth += 36000

        point = Point(
            order_in_packet,
            distance_uncalibrated_mm * GRANULARITY_MM,
            reflectivity,
            point_time_stamp,
            point_azimuth,
            laser_data[order_in_packet][1],
        )
        data_points.append(point)
        order_in_packet += 1

    return data_points


def adjust_azimuth_and_interpolate(curr_block_azimuth: float, next_block_azimuth: float):
    # Adjust for an Azimuth rollover from 359.99° to 0°
    if next_block_azimuth < curr_block_azimuth:
        next_block_azimuth += 360

    # Determine the Azimuth Gap between data blocks
    AzimuthGap = next_block_azimuth - curr_block_azimuth

    # Initialize the Precision_Azimuth list
    Precision_Azimuth: list[float] = [0] * 32  # Assuming we need 32 elements based on the loop

    # Perform the interpolation using the timing firing
    K = 0
    while K < 31:
        # Interpolate
        Precision_Azimuth[K] = curr_block_azimuth + (AzimuthGap * 2.304 * K) / 55.296
        Precision_Azimuth[K + 1] = Precision_Azimuth[K]

        # Apply the azimuth offsets
        Precision_Azimuth[K] += laser_data[K][2]
        Precision_Azimuth[K + 1] += laser_data[K + 1][2]

        # Adjust for any rollover
        if Precision_Azimuth[K] >= 360:
            Precision_Azimuth[K] -= 360
        if Precision_Azimuth[K + 1] >= 360:
            Precision_Azimuth[K + 1] -= 360

        K += 2

    return Precision_Azimuth
