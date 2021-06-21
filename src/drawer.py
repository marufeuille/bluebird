import datetime
import argparse
from enum import Enum

import matplotlib.pyplot as plt
import pandas as pd

class SamplingRate(Enum):
    MONTH = 'M'
    WEEK = 'W'
    DAY = 'D'
    HOUR = 'h'


def draw_days_ago_graph(df: pd.DataFrame, output_path: str="/tmp/img.png",days_ago:int=1, sampling_rate: SamplingRate=SamplingRate.HOUR) -> None:
    target = df.resample(sampling_rate.value).mean()
    fig, axs = plt.subplots(2,1, figsize=(12, 8))
    for idx, name in enumerate(['temperature', 'humidity']):
        axs[idx].plot(target[name])
        axs[idx].set_title(name)
        ymax = max(target[name]) * 1.1
        ymin = min(min(target[name]), 0)
        axs[idx].set_ylim(ymin, ymax)
        axs[idx].grid()
    fig.savefig(output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input_csv', type=str, required=True)
    parser.add_argument('--output_path', type=str, required=False, default="img.png")
    parser.add_argument('--days_ago', type=int, required=False, default=1)
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, names=('datetime', 'temperature', 'humidity')) \
            .dropna().reset_index(drop=True)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    draw_days_ago_graph(df, output_path=args.output_path ,days_ago=args.days_ago)