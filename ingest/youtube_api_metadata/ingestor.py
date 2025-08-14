import boto3
import json
import os
import random
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import isodate


QUERY_LIST = ["triathlon", "triathlete"]
query_rand_int = random.randint(0,2)
QUERY_TERM = QUERY_LIST[query_rand_int]

MAX_RESULTS = 50



def get_secret(secret_name, region_name='us-east-1'):
    client = boto3.client('secretsmanager', region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    
    return response['SecretString']


secrets = get_secret("youtube-api-key")
API_KEY = secrets.get("YOUTUBE_API_KEY")

s3 = boto3.client("s3")
s3_bucket = os.environ["S3_BUCKET"]
SEEN_KEY = "deduplicate/ids.json"


random_hour = random.randint(0, 23)
random_minute = random.randint(0,59)
now = datetime.now()
end_time = (now - timedelta(days=7)).replace(hour=random_hour, minute=0, second=0, microsecond=0)
start_time = end_time - timedelta(hours=12)

published_after = start_time.isoformat("T") + "Z"
published_before = end_time.isoformat("T") + "Z"

# Build YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)


def load_seen_ids(bucket, key):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return set(json.loads(obj['Body'].read().decode('utf-8')))
    except s3.exceptions.NoSuchKey:
        return set()


def save_seen_ids(bucket, key, ids):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(list(ids))
    )


def upload_df_to_s3(df, bucket_name):
    # Create timestamp and path
    seen_ids = load_seen_ids(s3_bucket, SEEN_KEY)

    df_filtered = df[~df["video_id"].isin(seen_ids)]

    if df_filtered.empty:
        print('no new videos to upload')
        return

    new_seen_ids = seen_ids.union(df_filtered["video_id"].tolist())
    save_seen_ids(s3_bucket, SEEN_KEY, new_seen_ids)

    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    s3_key = f"youtube_shorts/triathlon/{now.year}/{now.month:02}/{now.day:02}/run-{timestamp_str}.csv"

    # Convert DataFrame to CSV in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload to S3
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=csv_buffer.getvalue()
    )

    print(f"Uploaded CSV to s3://{bucket_name}/{s3_key}")


def parse_duration(iso_str):
    try:
        return int(isodate.parse_duration(iso_str).total_seconds())
    except Exception:
        return 0

def get_subscribers(channel_ids):
    subs = {}
    for i in range(0, len(channel_ids), 50):
        chunk = list(channel_ids)[i:i+50]
        resp = youtube.channels().list(part='statistics', id=','.join(chunk)).execute()
        for ch in resp['items']:
            subs[ch['id']] = int(ch['statistics'].get('subscriberCount', 0))
    return subs

def collect_videos():
    videos = []
    channel_ids = set()

    search = youtube.search().list(
        q=QUERY_TERM,
        type='video',
        part='id',
        maxResults=MAX_RESULTS,
        videoDuration='short',
        regionCode='US',
        order='date',
        publishedAfter=published_after,
        publishedBefore=published_before
    ).execute()

    video_ids = [item['id']['videoId'] for item in search.get('items', [])]
    if not video_ids:
        print("No videos found.")
        return []

    details = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=','.join(video_ids)
    ).execute()

    for item in details['items']:
        duration = parse_duration(item['contentDetails']['duration'])
        if duration > 60:
            continue

        published_at = item['snippet']['publishedAt']
        published_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        days_old = (datetime.now() - published_dt).days
        if days_old == 0:
            continue

        views = int(item['statistics'].get('viewCount', 0))
        views_per_day = views / max(days_old, 1)

        channel_id = item['snippet']['channelId']
        channel_ids.add(channel_id)

        video = {
            'query_term': QUERY_TERM,
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'channel_id': channel_id,
            'published_at': published_at,
            'duration_sec': duration,
            'views': views,
            'likes': int(item['statistics'].get('likeCount', 0)),
            'views_per_day': round(views_per_day, 2),
            'url': f"https://youtube.com/shorts/{item['id']}"
        }
        videos.append(video)

    subs = get_subscribers(channel_ids)
    for v in videos:
        v['subscriber_count'] = subs.get(v['channel_id'], 0)

    return videos

def lambda_handler(event, context):
    try:
        data = collect_videos()
        if data:
            df = pd.DataFrame(data)
            print(df[['title', 'views', 'views_per_day', 'subscriber_count']])
            upload_df_to_s3(df, s3_bucket)
            return {
                "statusCode": 200,
                "body": "uploaded data"
            }
        else:
            return {
                "statusCode": 200,
                "body": "No data"
            }
    except Exception as e:
        return {
            "error": str(e)
        }
