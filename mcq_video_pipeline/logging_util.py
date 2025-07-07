"""SQLite logging utilities."""
import sqlite3
from pathlib import Path
from typing import Dict

DB_FILE = Path("pipeline.db")


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            question TEXT,
            video_id TEXT,
            playlist_id TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def log_video(conn: sqlite3.Connection, data: Dict[str, str]) -> None:
    conn.execute(
        "INSERT INTO videos (subject, topic, question, video_id, playlist_id, status) VALUES (?, ?, ?, ?, ?, ?)",
        (
            data.get("Subject"),
            data.get("Topic"),
            data.get("Question"),
            data.get("video_id"),
            data.get("playlist_id"),
            data.get("status", "uploaded"),
        ),
    )
    conn.commit()
