
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# Load settings from the .env file
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

CREDENTIALS_FILE = "service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_sheets_service():
    """Connect to the Google Sheets API."""
    if not SPREADSHEET_ID or not SHEET_NAME:
        raise ValueError(
            "SPREADSHEET_ID and SHEET_NAME must be set in .env"
        )

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
    )

    return build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )


def add_transaction(
    transaction_type,
    amount,
    note="",
    need_or_want="",
    reason="",
):
    """Append a transaction to the spreadsheet."""

    service = get_sheets_service()

    # Use UK local time and the requested DD-MM-YYYY format.
    transaction_date = datetime.now(
        ZoneInfo("Europe/London")
    ).strftime("%d-%m-%Y")

    # Columns: Date | Income | Amount (Income) |
    # Expenses | Amount (Expenses) | Need or Want | Reason
    if transaction_type == "income":
        row = [
            transaction_date,
            note,
            amount,
            "",
            "",
            "",
            "",
        ]

    elif transaction_type == "expense":
        row = [
            transaction_date,
            "",
            "",
            note,
            amount,
            need_or_want,
            reason,
        ]

    else:
        raise ValueError("Invalid transaction type.")

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{SHEET_NAME}'!A:G",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={
            "values": [row]
        },
    ).execute()

    return True
