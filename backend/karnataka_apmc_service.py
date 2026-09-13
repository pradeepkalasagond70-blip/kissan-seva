import re

import pandas as pd

# Local Karnataka geography master.
# IMPORTANT: no ReMS website scraping happens at runtime. This keeps the
# Karnataka selector instant and stable in Streamlit/Cloud deployment.

KARNATAKA_MARKETS = {
    "Bengaluru": ["Bangalore"],
    "Bengaluru Rural": ["Doddaballapur", "Hoskote"],
    "Bengaluru South": ["Ramanagara"],
    "Ramanagara": ["Ramanagara"],
    "Chikkaballapur": ["Chikkaballapur"],
    "Chitradurga": ["Chitradurga", "Challakere", "Hiriyur", "Hosadurga", "Holalkere"],
    "Davanagere": ["Davanagere"],
    "Kolar": ["Kolar"],
    "Shivamogga": ["Shimoga", "Thirthahalli", "Sagar", "Hosanagar", "Soraba", "Shikaripur", "Bhadravathi"],
    "Tumakuru": ["Tumkur"],
    "Mysuru": ["Mysore"],
    "Chamarajanagar": ["Chamarajanagar"],
    "Dakshina Kannada": ["Mangalore"],
    "Udupi": ["Udupi"],
    "Kodagu": ["Madikeri"],
    "Chikkamagaluru": ["Chikkamagaluru"],
    "Hassan": ["Hassan"],
    "Mandya": ["Mandya"],
    "Belagavi": ["Belgaum", "Bailahongal", "Gokak", "Athani", "Kudachi", "Nippani", "Ramdurga", "Sankeshwara", "Savadatti"],
    "Vijayapura": ["Vijayapura"],
    "Bagalkote": ["Bagalkot"],
    "Dharwad": ["Dharwad", "Annigeri", "Hubli", "Kalaghatagi", "Kundagola"],
    "Gadag": ["Gadag"],
    "Haveri": ["Haveri", "Hanagal", "Byadagi", "Hirekerur", "Savanur", "Ranebennur", "Shiggaoan"],
    "Uttara Kannada": ["Karwar", "Honnavara", "Kumta", "Siddapur", "Sirsi", "Yellapur", "Haliyala", "Mundagod"],
    "Ballari": ["Bellary"],
    "Bidar": ["Bidar"],
    "Kalaburagi": ["Gulbarga"],
    "Koppal": ["Koppal", "Gangavathi", "Karatagi", "Kushtagi", "Yelburga"],
    "Raichur": ["Raichur", "Manvi", "Lingsugur", "Sindanur", "Devdurga"],
    "Yadgir": ["Yadgir"],
    "Vijayanagara": ["Hosapete"],
}

DISTRICT_ALIASES = {
    "bangalore": "Bengaluru",
    "bangalore rural": "Bengaluru Rural",
    "bengaluru": "Bengaluru",
    "bengaluru rural": "Bengaluru Rural",
    "bengaluru south": "Bengaluru South",
    "ramnagar": "Ramanagara",
    "ramanagar": "Ramanagara",
    "belgaum": "Belagavi",
    "belagavi": "Belagavi",
    "bijapur": "Vijayapura",
    "vijayapura": "Vijayapura",
    "bellary": "Ballari",
    "ballari": "Ballari",
    "gulbarga": "Kalaburagi",
    "kalaburagi": "Kalaburagi",
    "shimoga": "Shivamogga",
    "shivamogga": "Shivamogga",
    "tumkur": "Tumakuru",
    "tumakuru": "Tumakuru",
    "davangare": "Davanagere",
    "davanagere": "Davanagere",
    "mysore": "Mysuru",
    "mysuru": "Mysuru",
    "chamarajanagar": "Chamarajanagar",
    "chanmarajanagar": "Chamarajanagar",
    "chikkamagalur": "Chikkamagaluru",
    "chikkamagaluru": "Chikkamagaluru",
    "dharwar": "Dharwad",
    "dharwad": "Dharwad",
    "bagalkot": "Bagalkote",
    "bagalkote": "Bagalkote",
    "yadagiri": "Yadgir",
    "yadgir": "Yadgir",
    "dakshina kannada": "Dakshina Kannada",
    "dakshina-kannada": "Dakshina Kannada",
    "uttara kannda": "Uttara Kannada",
    "uttara kannada": "Uttara Kannada",
    "uttara-kannada": "Uttara Kannada",
    "vijayanagara": "Vijayanagara",
}


def canonical_district(value):
    key = re.sub(r"\s+", " ", str(value or "").strip()).casefold()
    return DISTRICT_ALIASES.get(key, str(value or "").strip())


def normalize_market(value):
    value = str(value or "").strip().casefold()
    value = re.sub(r"\b(a\.?p\.?m\.?c|market|yard)\b", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def load_karnataka_apmc_master():
    """Return a local Karnataka district/APMC master instantly."""
    rows = []
    for district, markets in KARNATAKA_MARKETS.items():
        for market in markets:
            rows.append({
                "state": "Karnataka",
                "district": district,
                "market": market,
                "master_source": "Karnataka local geography master",
            })

    return pd.DataFrame(
        rows,
        columns=["state", "district", "market", "master_source"],
    ).drop_duplicates(subset=["district", "market"]).sort_values(
        ["district", "market"]
    ).reset_index(drop=True)


def merge_karnataka_current_prices(master_df, current_df):
    """Left-join current government observations onto the local master."""
    master = master_df.copy()
    current = current_df.copy()

    for col in ["state", "district", "market"]:
        if col not in master:
            master[col] = ""
        if col not in current:
            current[col] = ""

    master["district_key"] = master["district"].map(canonical_district).str.casefold()
    master["market_key"] = master["market"].map(normalize_market)
    current["district_key"] = current["district"].map(canonical_district).str.casefold()
    current["market_key"] = current["market"].map(normalize_market)

    current_keys = set(zip(current["district_key"], current["market_key"]))
    missing = master[
        master["market_key"].ne("")
        & ~master.apply(
            lambda r: (r["district_key"], r["market_key"]) in current_keys,
            axis=1,
        )
    ].copy()

    if not missing.empty:
        for col in current.columns:
            if col not in missing.columns:
                missing[col] = pd.NA
        missing["state"] = "Karnataka"
        missing["master_only"] = True
        for col in ["commodity", "variety", "grade", "arrival_date"]:
            missing[col] = ""
        for col in ["min_price", "max_price", "modal_price"]:
            missing[col] = pd.NA
        current = pd.concat(
            [current, missing[current.columns]],
            ignore_index=True,
            sort=False,
        )

    current["master_only"] = current.get("master_only", False)
    return current.drop(
        columns=["district_key", "market_key"], errors="ignore"
    ).reset_index(drop=True)
