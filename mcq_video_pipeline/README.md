# MCQ Video Pipeline

This directory contains a modular pipeline for generating multiple-choice question explainer videos and uploading them to YouTube.

## Directory Structure

```
mcq_video_pipeline/
│   main.py                 # Entry point for generating videos
│   data_retrieval.py       # Load questions from Google Sheets
│   content_generation.py   # Build narration scripts
│   voiceover.py            # Text-to-speech utilities
│   video_creation.py       # Assemble video clips with moviepy
│   upload.py               # Upload videos to YouTube and Google Drive
│   playlist.py             # Playlist creation and management
│   logging_util.py         # SQLite logging helpers
│   email_notification.py   # Send status emails
│   requirements.txt        # Python dependencies
└── README.md
```

### Setup
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in this directory with your API keys and credentials. Example:
   ```bash
   GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
   GOOGLE_SHEETS_URL=https://docs.google.com/...
   YOUTUBE_CLIENT_SECRETS=client_secrets.json
   EMAIL_SENDER=you@example.com
   EMAIL_PASSWORD=your-email-password
   EMAIL_RECEIVER=notify@example.com
   ELEVEN_LABS_KEY=optional-elevenlabs
   ```

### Running
Run the pipeline manually with:
```bash
python main.py
```
To automate daily processing of five new videos, configure a cron job or GitHub Action that calls `python main.py` each day.

### Module Overview
- **data_retrieval.py** – Connects to Google Sheets using gspread and fetches new rows for processing.
- **content_generation.py** – Builds text scripts from the question, explanation, and strategy tip fields.
- **voiceover.py** – Generates speech audio with gTTS or ElevenLabs.
- **video_creation.py** – Creates videos with intro/outro branding, text slides, countdown timer, and embeds voiceover using moviepy.
- **upload.py** – Handles YouTube upload, Google Drive backup, and returns the video ID.
- **playlist.py** – Checks if a playlist exists for the subject, creates one if needed, and adds the video to it.
- **logging_util.py** – Records processing status and video metadata to an SQLite database.
- **email_notification.py** – Sends an email with the video link and playlist after successful upload.

This scaffold provides a starting point. Fill in each module with your desired logic to create a fully automated educational YouTube pipeline.
