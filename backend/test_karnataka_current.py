import requests
import json


# =========================================================
# CONFIG
# =========================================================

RESOURCE_ID = (
    "9ef84268-d588-465a-a308-a864a43d0070"
)

API_URL = (
    f"https://api.data.gov.in/resource/"
    f"{RESOURCE_ID}"
)


# =========================================================
# API KEY
# =========================================================
#
# IMPORTANT:
# Put your existing data.gov.in API key here.
# Do NOT paste the key into this chat.
#

API_KEY = "YOUR_API_KEY_HERE"


# =========================================================
# REQUEST
# =========================================================

params = {
    "api-key": API_KEY,
    "format": "json",

    # Karnataka only
    "filters[state]": "Karnataka",

    # Get a reasonable sample
    "limit": 100,
}


print("\n========================================")
print("KISSAN SEVA - KARNATAKA CURRENT PRICES")
print("========================================")


try:

    response = requests.get(
        API_URL,
        params=params,
        timeout=90,
    )

    print(
        "\nHTTP STATUS:",
        response.status_code,
    )

    print(
        "REQUEST URL:",
        response.url.replace(
            API_KEY,
            "***HIDDEN***"
        ),
    )

    response.raise_for_status()

    data = response.json()

except Exception as exc:

    print(
        "\nAPI REQUEST FAILED:"
    )

    print(exc)

    raise SystemExit


# =========================================================
# BASIC RESPONSE INFO
# =========================================================

print(
    "\nTOTAL RECORDS REPORTED:",
    data.get("total"),
)


records = data.get(
    "records",
    []
)


print(
    "RECORDS RECEIVED:",
    len(records),
)


# =========================================================
# NO RECORDS
# =========================================================

if not records:

    print(
        "\nNO KARNATAKA RECORDS RETURNED."
    )

    print(
        "\nFULL RESPONSE:"
    )

    print(
        json.dumps(
            data,
            indent=2
        )[:5000]
    )

    raise SystemExit


# =========================================================
# SHOW FIELD NAMES
# =========================================================

print(
    "\nFIELDS:"
)

print(
    list(records[0].keys())
)


# =========================================================
# SHOW FIRST 10 RECORDS
# =========================================================

print(
    "\n========================================"
)

print(
    "FIRST 10 KARNATAKA RECORDS"
)

print(
    "========================================"
)


for index, record in enumerate(
    records[:10],
    start=1
):

    print(
        f"\n--- RECORD {index} ---"
    )

    print(
        "State:",
        record.get("state")
    )

    print(
        "District:",
        record.get("district")
    )

    print(
        "Market:",
        record.get("market")
    )

    print(
        "Commodity:",
        record.get("commodity")
    )

    print(
        "Variety:",
        record.get("variety")
    )

    print(
        "Grade:",
        record.get("grade")
    )

    print(
        "Arrival Date:",
        record.get("arrival_date")
    )

    print(
        "Min Price:",
        record.get("min_price")
    )

    print(
        "Max Price:",
        record.get("max_price")
    )

    print(
        "Modal Price:",
        record.get("modal_price")
    )


# =========================================================
# UNIQUE DISTRICTS
# =========================================================

districts = sorted(
    {
        str(
            record.get(
                "district",
                ""
            )
        ).strip()

        for record in records

        if record.get("district")
    }
)


print(
    "\n========================================"
)

print(
    "DISTRICTS IN CURRENT SAMPLE"
)

print(
    "========================================"
)

print(
    "Count:",
    len(districts)
)

print(
    districts
)


# =========================================================
# UNIQUE COMMODITIES
# =========================================================

commodities = sorted(
    {
        str(
            record.get(
                "commodity",
                ""
            )
        ).strip()

        for record in records

        if record.get("commodity")
    }
)


print(
    "\n========================================"
)

print(
    "COMMODITIES IN CURRENT SAMPLE"
)

print(
    "========================================"
)

print(
    "Count:",
    len(commodities)
)

print(
    commodities
)


# =========================================================
# SUCCESS
# =========================================================

print(
    "\n========================================"
)

print(
    "CURRENT PRICE API TEST COMPLETE"
)

print(
    "========================================"
)