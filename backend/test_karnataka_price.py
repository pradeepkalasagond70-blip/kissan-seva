from backend.karnataka_price_service import (
    get_karnataka_state_id,
    get_karnataka_districts,
    get_karnataka_commodities,
    get_date_wise_commodity_history,
    _standardise_history,
)


# =========================================================
# KARNATAKA STATE
# =========================================================

print("\n--- KARNATAKA STATE ID ---")

state_id = get_karnataka_state_id()

print(
    "State ID:",
    state_id
)


# =========================================================
# KARNATAKA DISTRICTS
# =========================================================

print("\n--- KARNATAKA DISTRICTS ---")

districts = get_karnataka_districts()

print(
    "District count:",
    len(districts)
)

for district in districts:
    print(
        district["id"],
        "-",
        district["name"]
    )


# =========================================================
# KARNATAKA COMMODITIES
# =========================================================

print("\n--- KARNATAKA COMMODITIES ---")

commodities = get_karnataka_commodities()

print(
    "Commodity count:",
    len(commodities)
)


# =========================================================
# COMMON AGRICULTURAL COMMODITIES TO TEST
# =========================================================

test_commodities = [
    "Tomato",
    "Onion",
    "Potato",
    "Cotton",
    "Maize",
    "Wheat",
    "Green Chilli",
    "Groundnut",
    "Turmeric",
    "Chilli",
]


print(
    "\n--- TESTING RECENT KARNATAKA DATA ---"
)


successful_commodities = []


for commodity_name in test_commodities:

    # -----------------------------------------------------
    # Find commodity ID
    # -----------------------------------------------------

    commodity_match = None

    for item in commodities:

        if (
            item["name"].strip().casefold()
            == commodity_name.strip().casefold()
        ):

            commodity_match = item

            break

    if commodity_match is None:

        print(
            f"\n{commodity_name}: "
            "NOT FOUND IN AGMARKNET COMMODITY LIST"
        )

        continue

    commodity_id = commodity_match["id"]

    print(
        f"\nChecking: "
        f"{commodity_name} "
        f"(ID: {commodity_id})"
    )

    # -----------------------------------------------------
    # September 2026
    # -----------------------------------------------------

    df = get_date_wise_commodity_history(
        year=2026,
        month=9,
        state_id=state_id,
        commodity_id=commodity_id,
    )

    # -----------------------------------------------------
    # If September has no records,
    # try August 2026
    # -----------------------------------------------------

    if df.empty:

        print(
            "September 2026: "
            "No records"
        )

        df = get_date_wise_commodity_history(
            year=2026,
            month=8,
            state_id=state_id,
            commodity_id=commodity_id,
        )

        if df.empty:

            print(
                "August 2026: "
                "No records"
            )

            continue

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print(
        "Records received:",
        len(df)
    )

    df = _standardise_history(df)

    print(
        "Columns:",
        df.columns.tolist()
    )

    print(
        "\nSample records:"
    )

    print(
        df.head(5).to_string(
            index=False
        )
    )

    successful_commodities.append(
        commodity_name
    )


# =========================================================
# SUMMARY
# =========================================================

print(
    "\n========================================"
)

print(
    "TEST SUMMARY"
)

print(
    "========================================"
)

print(
    "Karnataka districts:",
    len(districts)
)

print(
    "AGMARKNET commodities:",
    len(commodities)
)

print(
    "Commodities with recent data:",
    len(successful_commodities)
)

print(
    successful_commodities
)

print(
    "========================================"
)