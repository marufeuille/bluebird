from abc import ABCMeta, abstractmethod
from collections import namedtuple
from os import PathLike
from typing import List, Optional
from datetime import datetime


SensorData = namedtuple('SensorData', ['datetime', 'temperature', 'humidity'])

class SensorDataInterface(metaclass=ABCMeta):
    @abstractmethod
    def save(self, data: SensorData) -> None:
        pass

    @abstractmethod
    def fetch_data(self, from_datetime: datetime, to_time: datetime, export_file_path: Optional[PathLike] = None) -> Optional[List[SensorData]]:
        pass

    @abstractmethod
    def get_latest_data(self) -> SensorData:
        pass