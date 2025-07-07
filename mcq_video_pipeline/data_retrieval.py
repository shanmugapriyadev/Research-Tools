"""Module to load MCQ data from Google Sheets."""
from typing import List, Dict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")


def fetch_rows(limit: int = 5) -> List[Dict[str, str]]:
    """Fetch rows from Google Sheets and return a list of dictionaries."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, scope
    )
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_url(SHEETS_URL).sheet1
    rows = sheet.get_all_records()
    return rows[:limit]
