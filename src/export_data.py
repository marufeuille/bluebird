from datetime import datetime, timedelta
import sqlite3
import pandas as pd

if __name__ == '__main__':
    con = sqlite3.connect('medaka.sqlite')
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
    days_ago = today - timedelta(days=1)
    df = pd.read_sql_query(f'SELECT * FROM medaka01 WHERE datetime < \'{today}\' AND datetime > \'{days_ago}\'', con)
    df['device'] = 'genkan'
    df.columns = ['observed_time', 'temperature', 'humidity', 'device']
    df['observed_time'] = pd.to_datetime(df['observed_time']).dt.tz_localize('Asia/Tokyo')
    df.to_gbq('medaka.medaka', if_exists='append', table_schema=[
        {'name': 'observed_time', 'type': 'DATETIME', 'mode': 'REQUIRED'},
        {'name': 'temperature', 'type': 'FLOAT', 'mode': 'REQUIRED'},
        {'name': 'humidity', 'type': 'FLOAT', 'mode': 'REQUIRED'},
        {'name': 'device', 'type': 'STRING', 'mode': 'REQUIRED'}
    ])