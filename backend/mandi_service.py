import os
import sqlite3
from pathlib import Path

import requests
from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "karnataka_mandi.db"

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"


# =========================================================
# API KEY
# =========================================================

def _get_api_key():
    key = os.getenv("DATA_GOV_API_KEY")

    if key:
        return key

    try:
        import streamlit as st
        return st.secrets.get("DATA_GOV_API_KEY")
    except Exception:
        return None


# =========================================================
# KARNATAKA SQLITE
# =========================================================

def _get_karnataka_prices(
    district=None,
    market=None,
    commodity=None,
    limit=100,
    offset=0,
):
    """Read Karnataka mandi prices from the local SQLite database."""

    if not DB_PATH.exists():
        return {
            "status": "error",
            "message": "Karnataka mandi database not found.",
            "source": "karnataka_sqlite",
            "total": 0,
            "count": 0,
            "offset": int(offset),
            "records": [],
        }

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conditions = ["state = ?"]
    values = ["Karnataka"]

    if district:
        conditions.append("district = ?")
        values.append(district)

    if market:
        conditions.append("market = ?")
        values.append(market)

    if commodity:
        conditions.append("commodity = ?")
        values.append(commodity)

    where_clause = " AND ".join(conditions)

    # Total matching records
    count_query = f"""
        SELECT COUNT(*)
        FROM mandi_prices
        WHERE {where_clause}
    """

    total = conn.execute(
        count_query,
        values
    ).fetchone()[0]

    # Actual records
    query = f"""
        SELECT
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
        FROM mandi_prices
        WHERE {where_clause}
        ORDER BY
            substr(arrival_date, 7, 4) DESC,
            substr(arrival_date, 4, 2) DESC,
            substr(arrival_date, 1, 2) DESC,
            market,
            commodity
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(
        query,
        values + [int(limit), int(offset)]
    ).fetchall()

    conn.close()

    records = [dict(row) for row in rows]

    return {
        "status": "success",
        "source": "karnataka_sqlite",
        "total": total,
        "count": len(records),
        "offset": int(offset),
        "records": records,
    }


# =========================================================
# GOVERNMENT API
# =========================================================

def _get_government_prices(
    state=None,
    district=None,
    market=None,
    commodity=None,
    limit=100,
    offset=0,
):
    """Fetch mandi prices directly from data.gov.in."""

    api_key = _get_api_key()

    if not api_key:
        raise ValueError(
            "DATA_GOV_API_KEY is not configured in .env"
        )

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": int(limit),
        "offset": int(offset),
    }

    if state:
        params["filters[state]"] = state

    if district:
        params["filters[district]"] = district

    if market:
        params["filters[market]"] = market

    if commodity:
        params["filters[commodity]"] = commodity

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers={
                "User-Agent": "Kissan-Seva/1.0"
            },
            timeout=(10, 60),
        )

        response.raise_for_status()

        data = response.json()

        records = data.get("records", [])

        return {
            "status": "success",
            "source": "data.gov.in",
            "total": data.get("total", 0),
            "count": len(records),
            "offset": int(offset),
            "records": records,
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Government mandi API timed out. Please try again.",
            "total": 0,
            "count": 0,
            "offset": int(offset),
            "records": [],
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Mandi API request failed: {str(e)}",
            "total": 0,
            "count": 0,
            "offset": int(offset),
            "records": [],
        }


# =========================================================
# MAIN FUNCTION
# =========================================================

def get_mandi_prices(
    state=None,
    district=None,
    market=None,
    commodity=None,
    limit=100,
    offset=0,
):
    """
    Karnataka → local SQLite database.

    Other states → data.gov.in API.
    """

    # Karnataka gets the accumulated local dataset
    if state and state.strip().lower() == "karnataka":
        return _get_karnataka_prices(
            district=district,
            market=market,
            commodity=commodity,
            limit=limit,
            offset=offset,
        )

    # Everything else keeps the existing API behavior
    return _get_government_prices(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        limit=limit,
        offset=offset,
    )


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n🌾 KISSAN SEVA MANDI SERVICE TEST")
    print("=" * 55)

    result = get_mandi_prices(
        state="Karnataka",
        limit=10,
    )

    print(f"Status : {result['status']}")
    print(f"Source : {result.get('source')}")
    print(f"Total  : {result['total']}")
    print(f"Count  : {result['count']}")

    print("\nRecords:")

    for record in result["records"]:
        print(
            record["district"],
            "|",
            record["market"],
            "|",
            record["commodity"],
            "|",
            record["arrival_date"],
            "|",
            record["modal_price"],
        )