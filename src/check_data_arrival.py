from datetime import datetime, timedelta
import argparse

import slackweb

from sqlite_sensor_data import SQliteSensorDataRepository

def check_data_arrival(latest_data_arrival_date: datetime, arrival_interval_minutes: int) -> bool:
    return datetime.now() - timedelta(minutes=arrival_interval_minutes) < latest_data_arrival_date


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    #parser.add_argument("--watch_file_path", type=str, required=True)
    parser.add_argument("--db_path", type=str, required=True)
    parser.add_argument("--data_ingestion_interval", type=int, required=True)
    parser.add_argument('--slack_webhook_url', type=str, required=True)
    args = parser.parse_args()

    sqlite_sensor_data_repository = SQliteSensorDataRepository(args.db_path)
    latest_arrival_data = sqlite_sensor_data_repository.get_latest_data()
    if not check_data_arrival(latest_arrival_data.datetime, args.data_ingestion_interval):
        slack = slackweb.Slack(url=args.slack_webhook_url)
        slack.notify(text=f"Error: could not get sensor data for more than {args.data_ingestion_interval}min")