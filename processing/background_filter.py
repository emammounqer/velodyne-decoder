from typing import Iterable
from itertools import islice
import numpy as np
import pandas as pd
import os
from decoder.frame import Frame, frame_to_csv


def background_filter(frames: Iterable[Frame]):
    z_th = (-5, 1)
    iou = 80
    azimuth_th = (850, 1650)
    dist_th = 1

    background_points = generate_background_points(frames, iou, z_th, azimuth_th)

    if not os.path.exists("out" + "\\BF"):
        os.makedirs("out" + "\\BF")
    background_points.to_csv("out" + "\\Backgroundpoints.csv", index=False)

    f = generate_background(
        frames,
        background_points,
        z_th,
        iou,
        dist_th,
    )
    for i, df in enumerate(f):
        df.to_csv("out" + "\\BF\\BackgroundF" + str(i) + ".csv", index=False)


def generate_background(frames: Iterable[Frame], background_points, z_th, iou, dist_th):
    for frame in frames:
        frame_to_csv(frame)
        df = generate_df_from_frame(frame)
        df = df[(df["z"] > z_th[0]) & (df["z"] < z_th[1]) & (df["distance_m"] < iou)]
        df["azimuth"] = df["azimuth"] / 100 // 0.20
        df = pd.merge(df, background_points, on=["azimuth", "laser_id"], how="left")
        df["distance_m_y"] = df["distance_m_y"].sub(df["distance_m_x"], fill_value=1)
        drop_index = df[df["distance_m_y"].abs() < dist_th].index
        df = df.drop(drop_index)
        yield df


def generate_background_points(
    frames: Iterable[Frame],
    iou: int,
    z_th: tuple[int, int],
    azimuth_th: tuple[int, int],
):

    li = []
    for frame in islice(frames, 100):
        print(frame.id)
        df = generate_df_from_frame(frame)
        df = df[(df["z"] > z_th[0]) & (df["z"] < z_th[1]) & (df["distance_m"] < iou)]
        df["azimuth"] = df["azimuth"] / 100 // 0.2
        df["azimuth"] = df["azimuth"].astype("int32")
        li.append(df)

    li = pd.concat(li, axis=0, ignore_index=True)
    li = li.sort_values(by=["azimuth", "laser_id", "frameID"])
    li["distance_m"] = np.round(li["distance_m"])
    li = li[["laser_id", "azimuth", "distance_m"]]
    BF = (
        li.groupby(["azimuth", "laser_id"])["distance_m"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )

    return BF


def generate_df_from_frame(frame: Frame):
    data = []
    for packet in frame.data:
        for data_block in packet.data_blocks:
            for data_point in data_block.data_points:
                data.append(
                    {
                        "z": data_point.z,
                        "x": data_point.x,
                        "y": data_point.y,
                        "laser_id": data_point.laser_id,
                        "azimuth": data_point.azimuth,
                        "distance_m": data_point.distance,
                        "reflectivity": data_point.reflectivity,
                        "time_stamp": packet.time_stamp,
                    }
                )
    df = pd.DataFrame(data)
    df["frameID"] = frame.id
    return df
