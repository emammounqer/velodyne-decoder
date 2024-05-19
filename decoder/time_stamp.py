import datetime
import struct


def get_time_stamp(packet_data: bytes):
    offset = 0x00F0
    size = 4
    timestamp_bytes = packet_data[offset : offset + size]
    return struct.unpack("<I", timestamp_bytes)[0]


def make_table(dual_mode):
    x_size = 12
    y_size = 32
    timing_offsets = [
        [0.0 for x in range(x_size)] for y in range(y_size)
    ]  # Init matrix
    # constants
    full_firing_cycle = 55.296  # µs
    single_firing = 2.304  # µs
    # compute timing offsets
    for x in range(x_size):
        for y in range(y_size):
            dataBlockIndex = x / 2 if dual_mode else x
            dataPointIndex = y / 2
            timing_offsets[y][x] = (full_firing_cycle * dataBlockIndex) + (
                single_firing * dataPointIndex
            )
    return timing_offsets


if __name__ == "__main__":
    print()

    # values = ["0c03ffee", "0c05ffee" ,"0c05ffee" ,"0d06ffee"]#, "0403ffee" ,"0001ffee"]
    # for value in values:
    #     print(value)
    #     time = int(value, 16) / 1e6
    #     print(time)
    #     print(datetime.datetime.fromtimestamp(time))
    #     print()

    timing_offsets = make_table(False)  # False : single return mode
    print(
        "\n".join(
            [
                ", ".join(["{:8.3f}".format(value) for value in row])
                for row in timing_offsets
            ]
        )
    )

    # out table to csv file
    with open("timing_offsets.csv", "w") as f:
        for row in timing_offsets:
            f.write(", ".join([str(value) for value in row]) + "\n")

    Timestamp = 45_231_878  # µs
    TimeOffset = timing_offsets[23][15]
    ExactPointTime = Timestamp + TimeOffset
    # ExactPointTime = 45,231,878 + 1,306.368 #µs
    # ExactPointTime = 45,233,184.368 #µs
