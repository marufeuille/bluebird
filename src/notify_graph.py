import argparse
import datetime
import pandas as pd
import json

from google.cloud import storage
from google.oauth2 import service_account
import slackweb

from drawer import draw_days_ago_graph
from sqlite_sensor_data import SQliteSensorDataRepository

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--output_path', type=str, required=False, default="img.png")
    parser.add_argument('--days_ago', type=int, required=False, default=1)
    parser.add_argument('--gcp_sa_json', type=str, required=False)
    parser.add_argument('--gcs_bucket_name', type=str, required=True)
    parser.add_argument('--gcs_project', type=str, required=True)
    parser.add_argument('--slack_webhook_url', type=str, required=True)
    parser.add_argument('--db_path', type=str, required=True)
    args = parser.parse_args()

    sqlite_sensor_data_repository = SQliteSensorDataRepository(args.db_path)
    now = datetime.datetime.now()
    today = datetime.datetime(year=now.year, month=now.month, day=now.day)
    days_ago = today - datetime.timedelta(days=args.days_ago)
    data = sqlite_sensor_data_repository.fetch_data(from_datetime=days_ago, to_datetime=today)
    
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    draw_days_ago_graph(df, output_path=args.output_path ,days_ago=args.days_ago)
    if args.gcp_sa_json is not None:
        with open(args.gcp_sa_json, "r") as f:
            creds = service_account.Credentials.from_service_account_info(json.load(f))
        client = storage.Client(args.gcs_project, credentials=creds)
    else:
        client = storage.Client(args.gcs_project)

    bucket = client.get_bucket(args.gcs_bucket_name)
    blob_path = f'{datetime.datetime.now().strftime("%Y%m%d")}/img.png'
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(args.output_path)

    slack = slackweb.Slack(url=args.slack_webhook_url)
    slack.notify(text=f"{blob.public_url}")