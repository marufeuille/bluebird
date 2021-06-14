import argparse
import datetime
import pandas as pd
import json

from google.cloud import storage
from google.oauth2 import service_account
import slackweb


from drawer import draw_days_ago_graph

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input_csv', type=str, required=True)
    parser.add_argument('--output_path', type=str, required=False, default="img.png")
    parser.add_argument('--days_ago', type=int, required=False, default=1)
    parser.add_argument('--gcp_sa_json', type=str, required=False)
    parser.add_argument('--gcs_bucket_name', type=str, required=True)
    parser.add_argument('--gcs_project', type=str, required=True)
    parser.add_argument('--slack_webhook_url', type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, names=('datetime', 'temperature', 'humidity')) \
            .dropna().reset_index(drop=True)
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