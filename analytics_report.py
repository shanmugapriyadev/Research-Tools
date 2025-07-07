from __future__ import annotations
"""Generate a simple weekly analytics report."""
import csv
import os
from datetime import datetime, timedelta
from typing import List

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_CLIENT_SECRETS")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def _fetch_recent_video_ids(days: int = 7) -> List[str]:
    """Return video IDs published in the last `days` days."""
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        part="id,snippet",
        channelId=CHANNEL_ID,
        maxResults=50,
        order="date",
    )
    response = request.execute()

    since = datetime.utcnow() - timedelta(days=days)
    video_ids = []
    for item in response.get("items", []):
        if item["id"].get("kind") != "youtube#video":
            continue
        published = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        if published >= since:
            video_ids.append(item["id"]["videoId"])
    return video_ids


def _fetch_stats(video_ids: List[str]) -> List[List[str]]:
    """Fetch statistics for each video ID."""
    if not video_ids:
        return []
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids))
    response = request.execute()

    rows = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        stats = item["statistics"]
        rows.append([
            snippet.get("title", ""),
            snippet.get("publishedAt", "")[:10],
            stats.get("viewCount", "0"),
            stats.get("likeCount", "0"),
            stats.get("commentCount", "0"),
        ])
    return rows


def generate_report(path: str = "weekly_report.csv") -> str:
    """Create a CSV report of videos published in the last 7 days."""
    ids = _fetch_recent_video_ids()
    data = _fetch_stats(ids)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Date", "Views", "Likes", "Comments"])
        writer.writerows(data)
    return path


if __name__ == "__main__":
    output = generate_report()
    print(f"Report saved to {output}")
