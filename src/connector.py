from collections import namedtuple
from typing import Optional
from time import sleep
import argparse
import datetime

from bluepy import btle

SensorData = namedtuple('SensorData', ['temperature', 'humidity'])

def get_ibsth1_mini_data(macaddr: str) -> Optional[SensorData]:
    try:
        peripheral = btle.Peripheral(macaddr)
        characteristic = peripheral.readCharacteristic(0x0028)
        temperature = int.from_bytes(characteristic[0:2], "little") / 100
        humidity = int.from_bytes(characteristic[2:4], "little") / 100
        return SensorData(temperature, humidity)
    except btle.BTLEDisconnectError:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--macaddr', type=str, required=True)
    parser.add_argument('--max_retry', type=int, required=False, default=5)
    parser.add_argument('--retry_after', type=int, required=False, default=5)
    args = parser.parse_args()
    max_retry: int = args.max_retry
    retry_after: int = args.retry_after
    for _ in range(max_retry):
        sensor_value = get_ibsth1_mini_data(args.macaddr)
        if sensor_value is not None:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {sensor_value.temperature}, {sensor_value.humidity}")
            break
        sleep(retry_after)
    else:
        print(f"Error: Exceeded Max Retry{max_retry}")
