"""Assemble video using moviepy."""
from pathlib import Path
from typing import Dict
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip,
)

INTRO_PATH = "assets/intro.mp4"
OUTRO_PATH = "assets/outro.mp4"


def create_video(row: Dict[str, str], audio_path: Path, out_path: Path) -> Path:
    question = row.get("Question", "")
    answer = row.get("Answer", "")
    explanation = row.get("Explanation", "")
    tip = row.get("Strategy Tip", "")

    intro = TextClip("Intro", fontsize=70, color="white", size=(1280, 720)).set_duration(3)
    outro = TextClip("Outro", fontsize=70, color="white", size=(1280, 720)).set_duration(3)

    question_clip = TextClip(question, fontsize=60, color="white", size=(1280, 720)).set_duration(5)
    answer_clip = TextClip(f"Answer: {answer}", fontsize=60, color="yellow", size=(1280, 720)).set_duration(3)
    explanation_clip = TextClip(explanation + " " + tip, fontsize=40, color="white", size=(1280, 720)).set_duration(8)

    audio = AudioFileClip(audio_path.as_posix())

    video = concatenate_videoclips([intro, question_clip, answer_clip, explanation_clip, outro])
    video = video.set_audio(audio)
    video.write_videofile(out_path.as_posix(), fps=24)
    return out_path
