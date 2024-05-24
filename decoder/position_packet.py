import re
import struct
from typing import NamedTuple, Optional


class NMEAData(NamedTuple):
    sentence: str
    time: str
    status: str
    latitude: float
    longitude: float
    speed: Optional[float]
    track_angle: Optional[float]
    date: str
    mag_var: Optional[float]
    mag_var_dir: Optional[str]
    fix_mode: Optional[str]
    checksum: str


class PositionData(NamedTuple):
    timestamp: int
    """
    The timestamp of the position packet in µs
    """

    pulse_per_second: int
    nmea_data: NMEAData | None


def parse_position_packet(packet_data: bytes) -> PositionData:
    if len(packet_data) != 554:
        raise ValueError("Position packet must be exactly 554 bytes.")
    time: int = struct.unpack_from("<I", packet_data, 0x00F0)[0]
    pulse_per_second = struct.unpack_from("<B", packet_data, 0x00F4)[0]

    return PositionData(time, pulse_per_second, parse_NMEA_data(packet_data))


def parse_NMEA_data(packet_data: bytes) -> NMEAData | None:
    start_of_nmea = 0x00F8

    end_of_nmea = packet_data.find(b"\x0D\x0A", start_of_nmea)
    if end_of_nmea == -1:
        return None

    nmea_gprmc_sentence = packet_data[start_of_nmea:end_of_nmea].decode("ascii")
    return parse_nmea(nmea_gprmc_sentence)


def parse_nmea(sentence: str) -> Optional[NMEAData]:
    # ^\$GPRMC,(?P<time>\d{6}(\.\d+)?),(?P<status>[AV]),(?P<latitude>\d{2}\d{2}\.\d+),(?P<lat_dir>[NS]),(?P<longitude>\d{3}\d{2}\.\d+),(?P<long_dir>[EW]),(?P<speed>\d+\.\d+)?,(?P<track_angle>\d+\.\d+)?,(?P<date>\d{6}),(?P<mag_var>\d+\.\d+)?,(?P<mag_var_dir>[EW])?,(?P<fix_mode>[ADEGNS]?)\*(?P<checksum>[A-F0-9]{2})
    pattern = re.compile(
        r"^\$GPRMC,"
        r"(?P<time>\d{6}(\.\d+)?),"
        r"(?P<status>[AV]),"
        r"(?P<latitude>\d{2}\d{2}\.\d+),(?P<lat_dir>[NS]),"
        r"(?P<longitude>\d{3}\d{2}\.\d+),(?P<long_dir>[EW]),"
        r"(?P<speed>\d+\.\d+)?,"
        r"(?P<track_angle>\d+\.\d+)?,"
        r"(?P<date>\d{6}),"
        r"(?P<mag_var>\d+\.\d+)?,(?P<mag_var_dir>[EW])?,"
        r"(?P<fix_mode>[ADEGNS]?)"
        r"\*(?P<checksum>[A-F0-9]{2})"
    )

    match = pattern.match(sentence)
    if not match:
        return None

    time = match.group("time")
    status = match.group("status")
    latitude = parse_coordinate(match.group("latitude"), match.group("lat_dir"))
    longitude = parse_coordinate(match.group("longitude"), match.group("long_dir"))
    speed = float(match.group("speed")) if match.group("speed") else None
    track_angle = float(match.group("track_angle")) if match.group("track_angle") else None
    date = match.group("date")
    mag_var = float(match.group("mag_var")) if match.group("mag_var") else None
    mag_var_dir = match.group("mag_var_dir")
    fix_mode = match.group("fix_mode")
    checksum = match.group("checksum")

    return NMEAData(
        sentence=sentence,
        time=time,
        status=status,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        track_angle=track_angle,
        date=date,
        mag_var=mag_var,
        mag_var_dir=mag_var_dir,
        fix_mode=fix_mode,
        checksum=checksum,
    )


def parse_coordinate(value, direction):
    degrees = int(value[:-7])
    minutes = float(value[-7:])
    coordinate = degrees + minutes / 60.0
    if direction in ["S", "W"]:
        coordinate = -coordinate
    return coordinate
