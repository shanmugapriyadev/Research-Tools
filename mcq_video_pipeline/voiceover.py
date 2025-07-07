"""Generate voiceover audio."""
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

from gtts import gTTS

try:
    from elevenlabs import generate
except Exception:
    generate = None

load_dotenv()

ELEVEN_LABS_KEY = os.getenv("ELEVEN_LABS_KEY")


def create_voiceover(text: str, out_path: Path) -> Path:
    """Create an MP3 voiceover using ElevenLabs if available, else gTTS."""
    if ELEVEN_LABS_KEY and generate:
        audio = generate(text=text, api_key=ELEVEN_LABS_KEY)
        with open(out_path, "wb") as f:
            f.write(audio)
    else:
        tts = gTTS(text)
        tts.save(out_path.as_posix())
    return out_path
