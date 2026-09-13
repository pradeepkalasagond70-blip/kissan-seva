import os
import sqlite3
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "karnataka_mandi.db"

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("DATA_GOV_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "DATA_GOV_API_KEY not found. "
        "Make sure your existing .env contains DATA_GOV_API_KEY."
    )


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS mandi_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    state TEXT NOT NULL,
    district TEXT,
    market TEXT,
    commodity TEXT,
    variety TEXT,
    grade TEXT,

    arrival_date TEXT,

    min_price REAL,
    max_price REAL,
    modal_price REAL,

    fetched_at TEXT,

    UNIQUE(
        state,
        district,
        market,
        commodity,
        variety,
        grade,
        arrival_date,
        min_price,
        max_price,
        modal_price
    )
);
"""


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()

    print(f"Database ready: {DB_PATH}")


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

def fetch_karnataka_page(offset=0, limit=1000):

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
        "filters[state]": "Karnataka",
    }

    response = requests.get(
        API_URL,
        params=params,
        headers={
            "User-Agent": "Kissan-Seva/1.0"
        },
        timeout=(15, 60),
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------------------------
# CLEAN RECORD
# ---------------------------------------------------------

def clean_record(record):

    def clean_text(value):
        if value is None:
            return None

        value = str(value).strip()

        if value.lower() in {
            "",
            "null",
            "none",
            "na",
            "n/a",
            "-"
        }:
            return None

        return value

    def clean_price(value):
        if value is None:
            return None

        try:
            value = str(value).replace(",", "").strip()
            return float(value)
        except (ValueError, TypeError):
            return None

    return {
        "state": clean_text(record.get("state")),
        "district": clean_text(record.get("district")),
        "market": clean_text(record.get("market")),
        "commodity": clean_text(record.get("commodity")),
        "variety": clean_text(record.get("variety")),
        "grade": clean_text(record.get("grade")),
        "arrival_date": clean_text(record.get("arrival_date")),
        "min_price": clean_price(record.get("min_price")),
        "max_price": clean_price(record.get("max_price")),
        "modal_price": clean_price(record.get("modal_price")),
    }


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

INSERT_SQL = """
INSERT OR IGNORE INTO mandi_prices (
    state,
    district,
    market,
    commodity,
    variety,
    grade,
    arrival_date,
    min_price,
    max_price,
    modal_price,
    fetched_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
"""


def save_records(records):

    if not records:
        return 0

    conn = sqlite3.connect(DB_PATH)

    inserted = 0

    for record in records:

        try:
            cursor = conn.execute(
                INSERT_SQL,
                (
                    record["state"],
                    record["district"],
                    record["market"],
                    record["commodity"],
                    record["variety"],
                    record["grade"],
                    record["arrival_date"],
                    record["min_price"],
                    record["max_price"],
                    record["modal_price"],
                ),
            )

            inserted += cursor.rowcount

        except sqlite3.Error as error:
            print(f"Database error: {error}")

    conn.commit()
    conn.close()

    return inserted


# ---------------------------------------------------------
# INGESTION
# ---------------------------------------------------------

def ingest_karnataka():

    print("\n🌾 KISSAN SEVA — KARNATAKA MANDI INGESTION")
    print("=" * 55)

    create_database()

    offset = 0
    page_size = 1000

    total_available = None
    total_fetched = 0
    total_inserted = 0

    while True:

        print(
            f"\nFetching Karnataka records "
            f"offset={offset}, limit={page_size}..."
        )

        try:
            data = fetch_karnataka_page(
                offset=offset,
                limit=page_size
            )

        except requests.exceptions.Timeout:
            print("❌ API request timed out.")
            print("Stopping safely.")
            break

        except requests.exceptions.RequestException as error:
            print(f"❌ API request failed: {error}")
            break

        records = data.get("records", [])

        if total_available is None:
            total_available = int(data.get("total", 0))

            print(
                f"Government API reports "
                f"{total_available} Karnataka records."
            )

        if not records:
            print("No more records returned.")
            break

        cleaned_records = []

        for record in records:

            cleaned = clean_record(record)

            # Safety check — only Karnataka goes into this DB.
            if cleaned["state"] != "Karnataka":
                continue

            cleaned_records.append(cleaned)

        inserted = save_records(cleaned_records)

        total_fetched += len(cleaned_records)
        total_inserted += inserted

        print(
            f"Received: {len(cleaned_records)} | "
            f"Inserted: {inserted} | "
            f"Fetched total: {total_fetched}"
        )

        if len(records) < page_size:
            print("Last page reached.")
            break

        offset += page_size

        # Avoid hammering the government API.
        time.sleep(0.5)

    print("\n" + "=" * 55)
    print("INGESTION COMPLETE")
    print("=" * 55)

    print(f"API reported records : {total_available}")
    print(f"Records fetched      : {total_fetched}")
    print(f"New records inserted : {total_inserted}")
    print(f"SQLite database      : {DB_PATH}")

    show_database_summary()


# ---------------------------------------------------------
# DATABASE SUMMARY
# ---------------------------------------------------------

def show_database_summary():

    conn = sqlite3.connect(DB_PATH)

    total = conn.execute(
        "SELECT COUNT(*) FROM mandi_prices"
    ).fetchone()[0]

    districts = conn.execute(
        "SELECT COUNT(DISTINCT district) FROM mandi_prices"
    ).fetchone()[0]

    markets = conn.execute(
        "SELECT COUNT(DISTINCT market) FROM mandi_prices"
    ).fetchone()[0]

    commodities = conn.execute(
        "SELECT COUNT(DISTINCT commodity) FROM mandi_prices"
    ).fetchone()[0]

    latest_date = conn.execute(
        "SELECT MAX(arrival_date) FROM mandi_prices"
    ).fetchone()[0]

    conn.close()

    print("\n📊 DATABASE SUMMARY")
    print("-" * 40)
    print(f"Total records : {total}")
    print(f"Districts     : {districts}")
    print(f"Markets       : {markets}")
    print(f"Commodities   : {commodities}")
    print(f"Latest date   : {latest_date}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    ingest_karnataka()