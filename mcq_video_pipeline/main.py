"""Entry point for MCQ video pipeline."""
from pathlib import Path
from data_retrieval import fetch_rows
from content_generation import build_script
from voiceover import create_voiceover
from video_creation import create_video
from upload import upload_to_youtube, backup_to_drive
from playlist import get_or_create_playlist, add_video_to_playlist
from logging_util import init_db, log_video
from email_notification import send_email

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_row(row):
    script = build_script(row)
    voice_path = OUTPUT_DIR / f"{row['Topic']}_narration.mp3"
    create_voiceover(script, voice_path)

    video_path = OUTPUT_DIR / f"{row['Topic']}.mp4"
    create_video(row, voice_path, video_path)

    video_id = upload_to_youtube(video_path, row['Topic'], row['Explanation'])
    backup_to_drive(video_path)

    playlist_id = get_or_create_playlist(row['Subject'])
    add_video_to_playlist(video_id, playlist_id)

    db = init_db()
    log_video(
        db,
        {
            "Subject": row["Subject"],
            "Topic": row["Topic"],
            "Question": row["Question"],
            "video_id": video_id,
            "playlist_id": playlist_id,
        },
    )

    send_email(
        "Video uploaded",
        f"Video: https://youtu.be/{video_id}\nPlaylist: {playlist_id}",
    )


def main():
    rows = fetch_rows(limit=5)
    for row in rows:
        process_row(row)


if __name__ == "__main__":
    main()
