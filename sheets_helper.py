import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_credentials = Credentials.from_service_account_file(config.GOOGLE_CREDS_FILE, scopes=SCOPES)
_client = gspread.authorize(_credentials)

HEADERS = ["Timestamp", "User ID", "User", "Harga", "Item", "Deskripsi", "Kategori"]


def _get_sheet():
    spreadsheet = _client.open_by_key(config.SPREADSHEET_ID)
    try:
        sheet = spreadsheet.worksheet("Expenses")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="Expenses", rows=1000, cols=10)

    first_row = sheet.row_values(1)
    if not first_row or first_row != HEADERS:
        sheet.update("A1:G1", [HEADERS])
        sheet.format("A1:G1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
        })

    return sheet


def add_expense(user_id: int, user_name: str, price: int, item: str, description: str | None, category: str) -> dict:
    sheet = _get_sheet()
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    row = [timestamp, str(user_id), user_name, price, item, description or "", category]
    sheet.append_row(row, value_input_option="USER_ENTERED")

    return {
        "timestamp": timestamp,
        "price": price,
        "item": item,
        "description": description,
        "category": category,
        "row_number": len(sheet.get_all_values()),
    }


def get_expenses_by_date_range(start_date: datetime, end_date: datetime, user_id: int = None) -> list[dict]:
    sheet = _get_sheet()
    all_rows = sheet.get_all_values()

    if len(all_rows) <= 1:
        return []

    expenses = []
    for row in all_rows[1:]:
        if len(row) < 7:
            continue
        try:
            row_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            if start_date <= row_date <= end_date:
                if user_id and row[1] != str(user_id):
                    continue
                expenses.append({
                    "timestamp": row[0],
                    "user_id": row[1],
                    "user_name": row[2],
                    "price": int(float(row[3])) if row[3] else 0,
                    "item": row[4],
                    "description": row[5],
                    "category": row[6],
                })
        except (ValueError, IndexError):
            continue

    return expenses


def get_today_expenses(user_id: int = None) -> list[dict]:
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return get_expenses_by_date_range(start, end, user_id)


def get_week_expenses(user_id: int = None) -> list[dict]:
    now = datetime.now()
    start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return get_expenses_by_date_range(start, end, user_id)


def get_month_expenses(user_id: int = None) -> list[dict]:
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return get_expenses_by_date_range(start, end, user_id)


def get_quarter_expenses(quarter: int, user_id: int = None) -> list[dict]:
    now = datetime.now()
    quarter_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}

    if quarter not in quarter_months:
        return []

    start_month, end_month = quarter_months[quarter]
    start = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)

    if end_month == 12:
        end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        end = now.replace(month=end_month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)

    return get_expenses_by_date_range(start, end, user_id)


def get_year_expenses(user_id: int = None) -> list[dict]:
    now = datetime.now()
    start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    return get_expenses_by_date_range(start, end, user_id)


def delete_last_entry(user_id: int = None) -> dict | None:
    sheet = _get_sheet()
    all_rows = sheet.get_all_values()

    if len(all_rows) <= 1:
        return None

    if user_id:
        for i in range(len(all_rows) - 1, 0, -1):
            row = all_rows[i]
            if len(row) >= 7 and row[1] == str(user_id):
                sheet.delete_rows(i + 1)
                return {
                    "timestamp": row[0],
                    "user_name": row[2],
                    "price": int(float(row[3])) if row[3] else 0,
                    "item": row[4],
                    "description": row[5],
                    "category": row[6],
                }
        return None

    last_row = all_rows[-1]
    last_row_number = len(all_rows)
    sheet.delete_rows(last_row_number)

    return {
        "timestamp": last_row[0] if len(last_row) > 0 else "",
        "user_name": last_row[2] if len(last_row) > 2 else "",
        "price": int(float(last_row[3])) if len(last_row) > 3 and last_row[3] else 0,
        "item": last_row[4] if len(last_row) > 4 else "",
        "description": last_row[5] if len(last_row) > 5 else "",
        "category": last_row[6] if len(last_row) > 6 else "",
    }
