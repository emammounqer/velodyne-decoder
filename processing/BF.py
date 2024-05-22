import numpy as np
import pandas as pd
import glob
import os


def backgroundfilter(path):
    all_files = sorted(glob.glob(os.path.join(path, "*.csv")), key=os.path.getmtime)
    parent_directory = os.path.dirname(path)
    if not os.path.exists(parent_directory + "\BF"):
        os.makedirs(parent_directory + "\BF")
    Zthre = [-5, 1]
    Iou = 80
    # Iou = 50
    # Azumith = [850, 1650]
    disthre = 1
    BaseIndex = [i for i in range(0, 3000, 50)]  # sampling index
    li = []
    for i, filename in enumerate(all_files):
        if i in BaseIndex:
            df = pd.read_csv(filename, index_col=None)
            df["frameID"] = i
            df = df[
                (df["Z"] > Zthre[0]) & (df["Z"] < Zthre[1]) & (df["distance_m"] < Iou)
            ]
            df["azimuth"] = df["azimuth"] / 100 // 0.2
            # df = df[(df['azimuth'] > Azumith[0]) & (df['azimuth'] < Azumith[1])]
            df["azimuth"] = df["azimuth"].astype("int32")
            li.append(df)
        else:
            continue

    li = pd.concat(li, axis=0, ignore_index=True)
    li = li.sort_values(by=["azimuth", "laser_id", "frameID"])
    li["distance_m"] = np.round(li["distance_m"])
    li = li[["laser_id", "azimuth", "distance_m"]]
    BF = (
        li.groupby(["azimuth", "laser_id"])["distance_m"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    BF.to_csv(parent_directory + "\Backgroundpoints.csv")

    for frame, filename in enumerate(all_files):
        df = pd.read_csv(filename, index_col=None)
        df = df[(df["Z"] > Zthre[0]) & (df["Z"] < Zthre[1]) & (df["distance_m"] < Iou)]
        df["azimuth"] = df["azimuth"] / 100 // 0.20
        # df = df[(df['azimuth'] > Azumith[0]) & (df['azimuth'] < Azumith[1])]
        df = pd.merge(df, BF, on=["azimuth", "laser_id"], how="left")
        df["distance_m_y"] = df["distance_m_y"].sub(df["distance_m_x"], fill_value=1)
        dropindex = df[df["distance_m_y"].abs() < disthre].index
        df = df.drop(dropindex)
        df = df.drop(["distance_m_y"], axis=1)
        df.to_csv(
            parent_directory + "\BF\BackgroundF" + str(frame) + ".csv", index=False
        )
    return parent_directory + "\BF"
