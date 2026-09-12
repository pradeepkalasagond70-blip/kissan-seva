import os
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

def _get_api_key():
    key = os.getenv("DATA_GOV_API_KEY")
    if key:
        return key

    try:
        import streamlit as st
        return st.secrets.get("DATA_GOV_API_KEY")
    except Exception:
        return None

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"


# --------------------------------------------------
# Get Mandi Prices
# --------------------------------------------------

def get_mandi_prices(
    state=None,
    district=None,
    market=None,
    commodity=None,
    limit=100
):
    """
    Fetch current mandi prices from the Government of India's
    data.gov.in API.
    """

    # Check API key
    api_key = _get_api_key()

    if not api_key:
        raise ValueError(
            "DATA_GOV_API_KEY is not configured in .env"
        )

    # API parameters
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": limit
    }

    # Optional filters
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
            timeout=(10, 60)
        )

        response.raise_for_status()

        data = response.json()

        records = data.get("records", [])

        return {
            "status": "success",
            "total": data.get("total", 0),
            "count": len(records),
            "records": records
        }

    except requests.exceptions.Timeout:

        return {
            "status": "error",
            "message": "Government mandi API timed out. Please try again.",
            "total": 0,
            "count": 0,
            "records": []
        }

    except requests.exceptions.RequestException as e:

        return {
            "status": "error",
            "message": f"Mandi API request failed: {str(e)}",
            "total": 0,
            "count": 0,
            "records": []
        }


# --------------------------------------------------
# Local Test
# --------------------------------------------------

if __name__ == "__main__":

    result = get_mandi_prices(
        commodity="Green Chilli",
        limit=5
    )

    print(result)