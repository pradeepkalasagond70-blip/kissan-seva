import requests
import pandas as pd

from datetime import date, timedelta
from functools import lru_cache


# =========================================================
# AGMARKNET CONFIGURATION
# =========================================================

AGMARKNET_BASE_URL = "https://api.agmarknet.gov.in/v1"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
}

# AGMARKNET Karnataka state ID
KARNATAKA_STATE_ID = 16


# =========================================================
# BASIC GET REQUEST
# =========================================================

def _get(url, params=None, timeout=30):

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=timeout,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# NORMALISE TEXT
# =========================================================

def _normalise(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .casefold()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "")
    )


# =========================================================
# EXTRACT RECORDS FROM API RESPONSE
# =========================================================

def _extract_records(data):

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in [
        "data",
        "records",
        "result",
        "results",
        "response",
    ]:

        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):

            nested = _extract_records(value)

            if nested:
                return nested

    return []


# =========================================================
# GET AGMARKNET FILTERS
# =========================================================

@lru_cache(maxsize=1)
def get_agmarknet_filters():

    url = (
        f"{AGMARKNET_BASE_URL}"
        "/daily-price-arrival/filters"
    )

    return _get(url)


# =========================================================
# GET FILTER CONTAINER
# =========================================================

def _get_filter_container(data):

    if not isinstance(data, dict):
        return {}

    if (
        "data" in data
        and isinstance(data["data"], dict)
    ):
        return data["data"]

    return data


# =========================================================
# KARNATAKA STATE ID
# =========================================================

def get_karnataka_state_id():

    return KARNATAKA_STATE_ID


# =========================================================
# KARNATAKA DISTRICTS
# =========================================================

def get_karnataka_districts():

    filters = _get_filter_container(
        get_agmarknet_filters()
    )

    districts = filters.get(
        "district_data",
        []
    )

    output = []

    for item in districts:

        if not isinstance(item, dict):
            continue

        try:

            state_id = int(
                item.get(
                    "state_id",
                    -1,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        if state_id != KARNATAKA_STATE_ID:
            continue

        district_id = item.get("id")

        district_name = item.get(
            "district_name"
        )

        if district_id is None:
            continue

        if not district_name:
            continue

        output.append(
            {
                "id": district_id,
                "name": str(
                    district_name
                ).strip(),
            }
        )

    output.sort(
        key=lambda x: x["name"].casefold()
    )

    return output


# =========================================================
# ALL AGMARKNET COMMODITIES
# =========================================================

def get_karnataka_commodities():

    filters = _get_filter_container(
        get_agmarknet_filters()
    )

    commodities = filters.get(
        "cmdt_data",
        []
    )

    output = []

    for item in commodities:

        if not isinstance(item, dict):
            continue

        commodity_id = item.get(
            "cmdt_id"
        )

        commodity_name = item.get(
            "cmdt_name"
        )

        if commodity_id is None:
            continue

        if not commodity_name:
            continue

        output.append(
            {
                "id": commodity_id,
                "name": str(
                    commodity_name
                ).strip(),
            }
        )

    output.sort(
        key=lambda x: x["name"].casefold()
    )

    return output


# =========================================================
# HISTORICAL DATE-WISE COMMODITY DATA
# =========================================================

def get_date_wise_commodity_history(
    year,
    month,
    state_id,
    commodity_id,
):

    url = (
        f"{AGMARKNET_BASE_URL}"
        "/prices-and-arrivals/date-wise/"
        "specific-commodity"
    )

    # IMPORTANT:
    # AGMARKNET expects stateId and commodityId.
    params = {
        "year": year,
        "month": month,
        "stateId": state_id,
        "commodityId": commodity_id,
        "includeExcel": "false",
    }

    try:

        data = _get(
            url,
            params=params,
            timeout=30,
        )

        records = _extract_records(data)

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    except requests.HTTPError as exc:

        print(
            "\n========================================"
        )

        print(
            "AGMARKNET HISTORICAL REQUEST FAILED"
        )

        print(
            "========================================"
        )

        if exc.response is not None:

            print(
                "Status:",
                exc.response.status_code,
            )

            print(
                "URL:",
                exc.response.url,
            )

            print(
                "\nResponse:"
            )

            print(
                exc.response.text[:2000]
            )

        print(
            "========================================\n"
        )

        return pd.DataFrame()

    except Exception as exc:

        print(
            "\nAGMARKNET historical request failed:",
            exc,
        )

        return pd.DataFrame()


# =========================================================
# STANDARDISE HISTORICAL DATA
# =========================================================

def _standardise_history(df):

    if df.empty:
        return df

    rename_map = {}

    for column in df.columns:

        key = _normalise(column)

        if key in {
            "arrivaldate",
            "date",
        }:

            rename_map[column] = (
                "arrival_date"
            )

        elif key in {
            "districtname",
            "district",
        }:

            rename_map[column] = (
                "district"
            )

        elif key in {
            "marketname",
            "market",
        }:

            rename_map[column] = (
                "market"
            )

        elif key in {
            "commodityname",
            "commodity",
            "cmdtname",
        }:

            rename_map[column] = (
                "commodity"
            )

        elif key in {
            "minprice",
            "minimumprice",
        }:

            rename_map[column] = (
                "min_price"
            )

        elif key in {
            "maxprice",
            "maximumprice",
        }:

            rename_map[column] = (
                "max_price"
            )

        elif key in {
            "modalprice",
            "modelprice",
            "modal",
        }:

            rename_map[column] = (
                "modal_price"
            )

    return df.rename(
        columns=rename_map
    )


# =========================================================
# GET LATEST SAME-DISTRICT PRICE
# =========================================================

def get_latest_karnataka_price(
    district,
    commodity,
    market=None,
):

    # -----------------------------------------------------
    # FIND DISTRICT
    # -----------------------------------------------------

    districts = get_karnataka_districts()

    district_match = None

    for item in districts:

        if (
            _normalise(item["name"])
            == _normalise(district)
        ):

            district_match = item
            break

    if district_match is None:

        print(
            "District not found:",
            district,
        )

        return None

    # -----------------------------------------------------
    # FIND COMMODITY
    # -----------------------------------------------------

    commodities = (
        get_karnataka_commodities()
    )

    commodity_match = None

    for item in commodities:

        if (
            _normalise(item["name"])
            == _normalise(commodity)
        ):

            commodity_match = item
            break

    if commodity_match is None:

        print(
            "Commodity not found:",
            commodity,
        )

        return None

    # -----------------------------------------------------
    # DATE RANGE
    # -----------------------------------------------------

    today = date.today()

    current_month = today.replace(
        day=1
    )

    previous_month = (
        current_month
        - timedelta(days=1)
    ).replace(
        day=1
    )

    months = [
        current_month,
        previous_month,
    ]

    frames = []

    # -----------------------------------------------------
    # REQUEST MONTHLY HISTORY
    # -----------------------------------------------------

    for month_start in months:

        print(
            f"Checking AGMARKNET: "
            f"{month_start.year}-"
            f"{month_start.month:02d} "
            f"{district} / {commodity}"
        )

        df = get_date_wise_commodity_history(
            year=month_start.year,
            month=month_start.month,
            state_id=KARNATAKA_STATE_ID,
            commodity_id=commodity_match[
                "id"
            ],
        )

        if not df.empty:

            frames.append(df)

    if not frames:

        print(
            "No historical records returned."
        )

        return None

    # -----------------------------------------------------
    # COMBINE
    # -----------------------------------------------------

    history = pd.concat(
        frames,
        ignore_index=True,
    )

    print(
        "Historical rows received:",
        len(history),
    )

    print(
        "Historical columns:",
        history.columns.tolist(),
    )

    # -----------------------------------------------------
    # STANDARDISE
    # -----------------------------------------------------

    history = _standardise_history(
        history
    )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [
        "arrival_date",
        "district",
        "market",
        "commodity",
        "modal_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in history.columns
    ]

    if missing_columns:

        print(
            "\nMissing historical columns:",
            missing_columns,
        )

        print(
            "Available columns:",
            history.columns.tolist(),
        )

        return None

    # -----------------------------------------------------
    # CLEAN DATE
    # -----------------------------------------------------

    history["arrival_date"] = pd.to_datetime(
        history["arrival_date"],
        errors="coerce",
        dayfirst=True,
    )

    # -----------------------------------------------------
    # CLEAN MODAL PRICE
    # -----------------------------------------------------

    history["modal_price"] = pd.to_numeric(
        history["modal_price"],
        errors="coerce",
    )

    # -----------------------------------------------------
    # CLEAN MIN PRICE
    # -----------------------------------------------------

    if "min_price" in history.columns:

        history["min_price"] = pd.to_numeric(
            history["min_price"],
            errors="coerce",
        )

    # -----------------------------------------------------
    # CLEAN MAX PRICE
    # -----------------------------------------------------

    if "max_price" in history.columns:

        history["max_price"] = pd.to_numeric(
            history["max_price"],
            errors="coerce",
        )

    # -----------------------------------------------------
    # REMOVE INVALID ROWS
    # -----------------------------------------------------

    history = history.dropna(
        subset=[
            "arrival_date",
            "modal_price",
        ]
    )

    # -----------------------------------------------------
    # SAME DISTRICT ONLY
    # -----------------------------------------------------

    history = history[
        history["district"]
        .astype(str)
        .map(_normalise)
        == _normalise(district)
    ]

    # -----------------------------------------------------
    # SAME COMMODITY ONLY
    # -----------------------------------------------------

    history = history[
        history["commodity"]
        .astype(str)
        .map(_normalise)
        == _normalise(commodity)
    ]

    if history.empty:

        print(
            "No records for the SAME district "
            "and commodity."
        )

        return None

    # -----------------------------------------------------
    # SAME MARKET PREFERRED
    # -----------------------------------------------------

    if market:

        market_history = history[
            history["market"]
            .astype(str)
            .map(_normalise)
            == _normalise(market)
        ]

        if not market_history.empty:

            history = market_history

    # -----------------------------------------------------
    # NEVER USE FUTURE DATA
    # -----------------------------------------------------

    history = history[
        history["arrival_date"].dt.date
        <= today
    ]

    if history.empty:

        return None

    # -----------------------------------------------------
    # NEWEST PRICE FIRST
    # -----------------------------------------------------

    history = history.sort_values(
        "arrival_date",
        ascending=False,
    )

    row = history.iloc[0]

    observation_date = (
        row["arrival_date"].date()
    )

    age_days = (
        today
        - observation_date
    ).days

    # -----------------------------------------------------
    # OPTIONAL MIN/MAX
    # -----------------------------------------------------

    min_price = None
    max_price = None

    if (
        "min_price" in row.index
        and pd.notna(row["min_price"])
    ):

        min_price = float(
            row["min_price"]
        )

    if (
        "max_price" in row.index
        and pd.notna(row["max_price"])
    ):

        max_price = float(
            row["max_price"]
        )

    # -----------------------------------------------------
    # RETURN SIMPLE PRICE RESULT
    # -----------------------------------------------------

    return {
        "district": str(
            row["district"]
        ).strip(),

        "market": str(
            row["market"]
        ).strip(),

        "commodity": str(
            row["commodity"]
        ).strip(),

        "arrival_date": (
            observation_date.isoformat()
        ),

        "age_days": age_days,

        "min_price": min_price,

        "max_price": max_price,

        "modal_price": float(
            row["modal_price"]
        ),

        "price_status": (
            "CURRENT"
            if age_days == 0
            else "HISTORICAL"
        ),
    }