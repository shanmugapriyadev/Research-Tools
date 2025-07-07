"""Manage YouTube playlists."""
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS")

youtube = build("youtube", "v3", developerKey=YOUTUBE_CLIENT_SECRETS)


def get_or_create_playlist(subject: str) -> str:
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    response = request.execute()
    for item in response.get("items", []):
        if item["snippet"]["title"] == subject:
            return item["id"]
    create_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": subject},
            "status": {"privacyStatus": "unlisted"},
        },
    )
    create_response = create_request.execute()
    return create_response.get("id")


def add_video_to_playlist(video_id: str, playlist_id: str) -> None:
    youtube.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
    ).execute()
