import os
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from gtts import gTTS
from moviepy.editor import (ImageClip, AudioFileClip, concatenate_videoclips,
                           TextClip, CompositeVideoClip)

# Optional: openai and youtube API imports; they require API keys
try:
    import openai
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    openai = None
    build = None


load_dotenv()

DATA_PATH = os.getenv("WORKFLOW_DATA", "data.xlsx")
DB_PATH = os.getenv("WORKFLOW_DB", "workflow.db")
OUTPUT_DIR = Path(os.getenv("WORKFLOW_OUT", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def load_questions(path: str) -> pd.DataFrame:
    """Load spreadsheet with questions."""
    return pd.read_excel(path)


def generate_script(row: pd.Series) -> str:
    """Generate narration script using OpenAI API if available."""
    if openai and OPENAI_KEY:
        openai.api_key = OPENAI_KEY
        prompt = (
            f"Create a short script for a question and answer video.\n"
            f"Subject: {row.get('subject')}\n"
            f"Topic: {row.get('topic')}\n"
            f"Question: {row.get('question')}\n"
            f"Answer: {row.get('answer')}\n"
            f"Explanation: {row.get('explanation')}\n"
            f"Strategy: {row.get('strategy tips')}\n"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
        )
        return response.choices[0].text.strip()
    # fallback to simple template
    return (
        f"In this video, we'll cover {row.get('topic')}. "
        f"Consider the following question: {row.get('question')} "
        f"The correct answer is {row.get('answer')}. "
        f"{row.get('explanation')} "
        f"Strategy tip: {row.get('strategy tips')}"
    )


def create_voiceover(text: str, path: Path) -> Path:
    """Create MP3 voiceover from text."""
    tts = gTTS(text)
    tts.save(path.as_posix())
    return path


def build_video(row: pd.Series, narration_path: Path, output_path: Path) -> Path:
    """Create a simple video with text and narration."""
    slides = []
    # intro slide
    title_clip = TextClip(f"{row.get('subject')} - {row.get('topic')}", fontsize=70,
                          color='white', bg_color='black', size=(1280, 720))
    title_clip = title_clip.set_duration(3)
    slides.append(title_clip)

    # question slide
    question_clip = TextClip(row.get('question'), fontsize=50,
                             color='white', bg_color='black', size=(1280, 720))
    question_clip = question_clip.set_duration(5)
    slides.append(question_clip)

    # answer slide
    answer_clip = TextClip(f"Answer: {row.get('answer')}", fontsize=60,
                           color='yellow', bg_color='black', size=(1280, 720))
    answer_clip = answer_clip.set_duration(4)
    slides.append(answer_clip)

    narration = AudioFileClip(narration_path.as_posix())
    video = concatenate_videoclips(slides).set_audio(narration)
    video.write_videofile(output_path.as_posix(), fps=24)
    return output_path


def upload_to_youtube(video_path: Path, title: str, description: str) -> str:
    """Upload video to YouTube and return video ID."""
    if not build:
        print("Google API client not available. Skipping upload.")
        return ""

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': []
        },
        'status': {
            'privacyStatus': 'unlisted'
        }
    }
    media = MediaFileUpload(video_path.as_posix(), mimetype='video/mp4')
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    return response.get('id')


def log_video(db: sqlite3.Connection, row: pd.Series, video_id: str):
    """Log uploaded video information to SQLite."""
    db.execute(
        "INSERT INTO videos (subject, topic, question, video_id, uploaded_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (row.get('subject'), row.get('topic'), row.get('question'), video_id, datetime.utcnow()),
    )
    db.commit()


def send_email(subject: str, body: str):
    """Send notification email."""
    if not (EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER):
        print("Email credentials missing. Skipping email notification.")
        return
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)


def ensure_db(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS videos (\n"
        " id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        " subject TEXT,\n"
        " topic TEXT,\n"
        " question TEXT,\n"
        " video_id TEXT,\n"
        " uploaded_at TIMESTAMP\n"
        ")"
    )
    return db


def process_row(row: pd.Series, db: sqlite3.Connection):
    script = generate_script(row)
    narration_file = OUTPUT_DIR / f"{row.name}_narration.mp3"
    create_voiceover(script, narration_file)

    video_file = OUTPUT_DIR / f"{row.name}_video.mp4"
    build_video(row, narration_file, video_file)

    video_id = upload_to_youtube(
        video_file,
        title=f"{row.get('topic')} question",
        description=row.get('explanation') or ""
    )

    log_video(db, row, video_id)
    send_email(
        "Video uploaded",
        f"Video ID: {video_id}\nTitle: {row.get('topic')}"
    )


def main():
    questions = load_questions(DATA_PATH)
    db = ensure_db(DB_PATH)
    for _, row in questions.iterrows():
        process_row(row, db)


if __name__ == "__main__":
    main()
