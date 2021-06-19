from datetime import datetime, timedelta
import argparse

import slackweb

def check_data_arrival(latest_data_arrival_date: datetime, arrival_interval_minutes: int) -> bool:
    return datetime.now() - timedelta(minutes=arrival_interval_minutes) < latest_data_arrival_date


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--watch_file_path", type=str, required=True)
    parser.add_argument("--data_ingestion_interval", type=int, required=True)
    parser.add_argument('--slack_webhook_url', type=str, required=True)
    args = parser.parse_args()

    with open(args.watch_file_path) as f:
        latest_arrival_date = datetime.strptime(f.readlines()[-1].split(",")[0], '%Y-%m-%d %H:%M:%S')
        if not check_data_arrival(latest_arrival_date, args.data_ingestion_interval):
            slack = slackweb.Slack(url=args.slack_webhook_url)
            slack.notify(text=f"Error: could not get sensor data for more than {args.data_ingestion_interval}min")