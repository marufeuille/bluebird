from typing import List
from os import PathLike
from pathlib import Path
from datetime import datetime
import sqlite3
from sensor_data_interface import SensorDataRepositoryInterface, SensorData


class SQliteSensorDataRepository(SensorDataRepositoryInterface):
    def __init__(self, dbfile: PathLike) -> None:
        self._con = sqlite3.connect(dbfile)
        self.time_format = "%Y-%m-%d %H:%M:%S"
    
    def save(self, data: SensorData) -> None:
        cur = self._con.cursor()
        cur.execute(f"""
        INSERT INTO medaka01 VALUES ('{data.datetime}', {data.temperature}, {data.humidity})
        """)
        self._con.commit()
    
    def fetch_data(self, from_datetime: datetime, to_datetime: datetime) -> List[SensorData]:
        cur = self._con.cursor()
        query = f"""
        SELECT
            datetime, temperature, humidity
        FROM
            medaka01
        WHERE
            datetime >= '{from_datetime}'
            AND datetime < '{to_datetime}'
        """
        results: List[SensorData] = []
        for row in cur.execute(query):
            results.append(
                SensorData(
                    datetime=datetime.strptime(row[0], self.time_format),
                    temperature=row[1],
                    humidity=row[2]
                )
            )

        return results       

    
    def get_latest_data(self) -> SensorData:
        cur = self._con.cursor()
        latest = cur.execute(
            f"""
            SELECT
                date, temperature, humidity
            FROM
                medaka01
            GROUP BY
                date
            HAVING
                date = max(date)
            """
        ).fetchall()[-1]
        return SensorData(
            datetime=datetime.strptime(latest[0], self.time_format),
            temperature=latest[1],
            humidity=latest[2]
        )
