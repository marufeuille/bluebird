from collections import namedtuple
from typing import cast
from time import sleep
from enum import Enum
import argparse
import datetime

import redis
import slackweb
from bluepy import btle

from sensor_data_interface import SensorData
from sqlite_sensor_data import SQliteSensorDataRepository

def get_ibsth1_data(macaddr: str) -> SensorData:
    try:
        peripheral = btle.Peripheral(macaddr)
        characteristic = peripheral.readCharacteristic(0x0028)
        temperature = int.from_bytes(characteristic[0:2], "little") / 100
        humidity = int.from_bytes(characteristic[2:4], "little") / 100
        now = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "%Y-%m-%d %H:%M:%S")
        return SensorData(now, temperature, humidity)
    except btle.BTLEDisconnectError:
        raise ConnectionError("Peripheral did not connect.")

class CompareOp(Enum):
    LT = "<"
    GT = ">"

def check_temperature(data: SensorData, threshold: float, op: CompareOp) -> bool:
    if op == CompareOp.GT:
        return data.temperature > threshold
    elif op == CompareOp.LT:
        return data.temperature < threshold
    else:
        raise AttributeError("op: {op} is not defined.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--macaddr', type=str, required=True)
    parser.add_argument('--max_retry', type=int, required=False, default=5)
    parser.add_argument('--retry_after', type=int, required=False, default=5)
    parser.add_argument('--slack_webhook_url', type=str, required=True)
    parser.add_argument('--redis_url', type=str, required=False, default="localhost")
    parser.add_argument('--redis_port',type=int, required=False, default=6379)
    parser.add_argument('--redis_db', type=int, required=False, default=0)
    parser.add_argument('--db_path', type=str, required=True, default=0)
    args = parser.parse_args()
    max_retry: int = args.max_retry
    retry_after: int = args.retry_after
    sensor_data_repo = SQliteSensorDataRepository(args.db_path)
    for _ in range(max_retry):
        try:
            sensor_value = get_ibsth1_data(args.macaddr)
            sensor_data_repo.save(sensor_value)
            print(f"{sensor_value.datetime}, {sensor_value.temperature}, {sensor_value.humidity}")
            
            # TODO: Parameterize
            if check_temperature(sensor_value, 28, CompareOp.GT):
                rds = redis.Redis(host=args.redis_url, port=args.redis_port, db=args.redis_db)
                value = rds.get("count")
                if value is None:
                    value = 1
                else:
                    value = int.from_bytes(cast(bytes, value), "big")
                    value = value + 1
                if value == 5:
                    slack = slackweb.Slack(url=args.slack_webhook_url)
                    slack.notify(text=f"temperature exceed 28C 5times")
                rds.set("count", value)
            else:
                rds = redis.Redis(host=args.redis_url, port=args.redis_port, db=args.redis_db)
                rds.set("count", 0)
            break
        except ConnectionError:
            sleep(retry_after)
    else:
        print(f"Error: Exceeded Max Retry{max_retry}")
