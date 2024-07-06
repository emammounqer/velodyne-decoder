import struct
from decoder.const import (
    GRANULARITY_MM,
    DATA_BLOCK_OFFSET,
    FULL_FIRING_CYCLE_TIME,
    SINGLE_FIRING_TIME,
    laser_data,
)
from typing import NamedTuple
import math
from numba import njit


class Point(NamedTuple):
    laser_id: int
    distance: int
    reflectivity: int
    timestamp: float
    azimuth: float
    """Azimuth angle in degrees"""
    vertical_angle: float
    """Vertical angle in degrees"""
    x: float
    y: float
    z: float

    def distance_m(self) -> float:
        return self.distance / 1000

    def distance_m_x(self) -> float:
        # TODO: Implement this
        return self.distance / 1000

    def distance_m_y(self) -> float:
        # TODO: Implement this
        return self.distance / 1000


class DataBlock(NamedTuple):
    block_index: int
    azimuth: int
    """Azimuth angle in hundredths of degrees"""
    data_points: list[Point]


def parse_data_block(
    packet_data: bytes,
    block_index: int,
    time_stamp: int,
    return_mode: int,
    factory_model: int,
) -> DataBlock:
    azimuth: int = struct.unpack_from(
        "< H", packet_data, 2 + DATA_BLOCK_OFFSET[block_index]
    )[0]

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
    for i in range(
        4 + DATA_BLOCK_OFFSET[block_index], 100 + DATA_BLOCK_OFFSET[block_index], 3
    ):
        distance_uncalibrated_mm, reflectivity = struct.unpack_from(
            "< H B", packet_data, i
        )
        if distance_uncalibrated_mm == 0:
            order_in_packet += 1
            continue

        distance = distance_uncalibrated_mm * GRANULARITY_MM
        offset_index = block_index // 2 if return_mode == 0x39 else block_index
        offset = (
            offset_index * FULL_FIRING_CYCLE_TIME
            + order_in_packet // 2 * SINGLE_FIRING_TIME
        )
        point_time_stamp = offset + time_stamp

        point_azimuth = azimuth / 100 + (laser_data[order_in_packet][2])
        if point_azimuth >= 360:
            point_azimuth -= 360
        if point_azimuth < 0:
            point_azimuth += 360

        vertical_angle = laser_data[order_in_packet][1]

        (x, y, z) = get_point_coordinates(distance, point_azimuth, vertical_angle)

        point = Point(
            order_in_packet,
            distance,
            reflectivity,
            point_time_stamp,
            point_azimuth,
            vertical_angle,
            x,
            y,
            z,
        )
        data_points.append(point)
        order_in_packet += 1

    return data_points


def adjust_azimuth_and_interpolate(
    curr_block_azimuth: float, next_block_azimuth: float
):
    # Adjust for an Azimuth rollover from 359.99° to 0°
    if next_block_azimuth < curr_block_azimuth:
        next_block_azimuth += 360

    # Determine the Azimuth Gap between data blocks
    AzimuthGap = next_block_azimuth - curr_block_azimuth

    # Initialize the Precision_Azimuth list
    Precision_Azimuth: list[float] = [
        0
    ] * 32  # Assuming we need 32 elements based on the loop

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


@njit
def get_point_coordinates(
    distance: float, azimuth: float, vertical_angle: float
) -> tuple[float, float, float]:
    x = (
        distance
        * math.cos(math.radians(vertical_angle))
        * math.sin(math.radians(azimuth))
    )
    y = (
        distance
        * math.cos(math.radians(vertical_angle))
        * math.cos(math.radians(azimuth))
    )
    z = distance * math.sin(math.radians(vertical_angle))
    return x, y, z
