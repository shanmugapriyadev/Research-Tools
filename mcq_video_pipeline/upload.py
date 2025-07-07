"""Upload video to YouTube and Google Drive."""
from pathlib import Path
from typing import Dict
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS")

# Placeholder for Google Drive implementation

def upload_to_youtube(video_path: Path, title: str, description: str) -> str:
    """Upload video and return the YouTube video ID."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_CLIENT_SECRETS)
    body = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "unlisted"},
    }
    media = MediaFileUpload(video_path.as_posix(), mimetype="video/mp4")
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = request.execute()
    return response.get("id")


def backup_to_drive(video_path: Path) -> None:
    """Upload a copy to Google Drive."""
    pass
