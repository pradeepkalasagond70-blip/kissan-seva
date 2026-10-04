import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
from textwrap import dedent

import sys
from pathlib import Path as _Path

PROJECT_ROOT = _Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.mandi_service import get_mandi_prices
import backend.mandi_service as _mandi_service
from backend.irrigation_service import get_irrigation_recommendation
from backend.model_service import price_prediction_service
from backend.karnataka_apmc_service import canonical_district, normalize_market

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Kissan Seva | Smarter Farming",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Backend services run inside the Streamlit deployment.
API_BASE = None

LINKEDIN_URL = "https://www.linkedin.com/in/pradeep-kalasagond-95579a230"

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

HERO_IMAGE = (
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef"
    "?auto=format&fit=crop&w=1800&q=85"
)


# Government mandi selector states.
# The app no longer calls the full India mandi dataset just to build this list.
SUPPORTED_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]


# ============================================================
# HTML HELPER
# Prevents indented HTML from being rendered as code blocks.
# ============================================================

def html(markup):
    st.html(dedent(markup).strip())


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background: #f7faf8;
}

.block-container {
    max-width: 1500px;
    padding-top: 0.35rem;
    padding-bottom: 1.5rem;
}

h1, h2, h3, h4 {
    color: #10261d;
}

/* ================= NAVBAR ================= */

.navbar {
    background: rgba(255,255,255,0.98);
    border-bottom: 1px solid #e3ebe6;
    padding: 10px 18px;
    border-radius: 0 0 14px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    margin-bottom: 10px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background: linear-gradient(135deg, #07894f, #64bd55);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
}

.brand-name {
    font-size: 24px;
    font-weight: 850;
    color: #10261d;
    line-height: 1;
}

.brand-tagline {
    color: #687870;
    font-size: 11px;
    margin-top: 4px;
}

.nav-wrap {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.nav-pill {
    display: inline-block;
    cursor: pointer;
    padding: 8px 11px;
    margin-left: 3px;
    border-radius: 9px;
    color: #33443d;
    font-size: 13px;
    font-weight: 650;
}

.nav-pill.active {
    background: #087f4f;
    color: white !important;
}

.nav-pill:hover {
    background: #edf7f1;
    color: #087f4f !important;
    text-decoration: none !important;
}

/* ================= HERO ================= */

.hero {
    height: 245px;
    border-radius: 0 0 22px 22px;
    overflow: hidden;
    position: relative;
    background:
        linear-gradient(
            90deg,
            rgba(5,38,25,0.86),
            rgba(5,55,35,0.58),
            rgba(5,40,25,0.18)
        ),
        url("__HERO_IMAGE__") center 52% / cover no-repeat;
    padding: 38px 44px;
    color: white;
    margin-bottom: 16px;
    box-shadow: 0 7px 24px rgba(25,70,48,0.10);
}

.hero-badge {
    display: inline-block;
    padding: 6px 14px;
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 22px;
    background: rgba(255,255,255,0.12);
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 0.7px;
}

.hero-title {
    font-size: 42px;
    font-weight: 850;
    margin-top: 18px;
    margin-bottom: 1px;
    color: white;
}

.hero-subtitle {
    font-size: 21px;
    font-weight: 750;
    color: white;
    margin-bottom: 5px;
}

.hero-description {
    font-size: 14px;
    max-width: 570px;
    line-height: 1.45;
    color: rgba(255,255,255,0.92);
}

.hero-quote {
    position: absolute;
    right: 40px;
    top: 55px;
    text-align: right;
    font-size: 17px;
    font-style: italic;
    color: white;
}

/* ================= FEATURE STRIP ================= */

.feature-link {
    display: block;
    color: inherit !important;
    text-decoration: none !important;
}

.feature-card {
    background: white;
    border: 1px solid #e1e9e4;
    border-radius: 14px;
    padding: 12px 10px;
    text-align: center;
    box-shadow: 0 3px 12px rgba(25,70,48,0.04);
    min-height: 92px;
}

.feature-icon {
    font-size: 23px;
}

.feature-title {
    font-weight: 800;
    font-size: 13px;
    margin-top: 2px;
    color: #193128;
}

.feature-sub {
    color: #718078;
    font-size: 11px;
}

.feature-icon-clean {
    width: 42px;
    height: 42px;
    margin: 0 auto 5px;
    border-radius: 50%;
    background: #eef8f2;
    color: #087f4f;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 800;
}

.feature-open {
    color: #087f4f;
    font-size: 10px;
    font-weight: 750;
    margin-top: 7px;
    opacity: 0;
    transition: opacity 0.15s ease;
}

.feature-link:hover .feature-card {
    border-color: #9ed4b8;
    transform: translateY(-1px);
}

.feature-link:hover .feature-open {
    opacity: 1;
}

/* ================= SECTIONS ================= */

.section-title {
    font-size: 23px;
    font-weight: 820;
    color: #10261d;
    margin-top: 15px;
    margin-bottom: 4px;
}

.section-description {
    color: #718078;
    font-size: 13px;
    margin-bottom: 12px;
}

/* ================= CARDS ================= */

 .info-link-card {
    display: block;
    color: inherit !important;
    text-decoration: none !important;
}

/* Premium feature-style resource cards */
.info-link-card .card {
    min-height: 200px;
    height: 200px;
    box-sizing: border-box;
    padding: 18px 16px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;
}

.info-link-card:hover .card {
    transform: translateY(-3px);
    border-color: #9ed4b8;
    box-shadow: 0 10px 24px rgba(25,70,48,.09);
}

.info-link-icon {
    width: 42px;
    height: 42px;
    margin: 0 auto 7px;
    border-radius: 50%;
    background: #eef8f2;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 21px;
    line-height: 1;
}

.info-link-card .card-title {
    font-size: 17px;
    font-weight: 800;
    margin-bottom: 5px;
}

.info-link-card .card p {
    font-size: 12px;
    line-height: 1.45;
    margin: 3px 0;
}

.info-link-card .resource-description {
    max-width: 340px;
    color: #738078;
}

.info-link-card .resource-list {
    color: #4f5f58;
}

.card-action {
    margin-top: auto;
    color: #087f4f;
    font-size: 11px;
    font-weight: 800;
}

.card {
    background: white;
    border: 1px solid #e1e9e4;
    border-radius: 16px;
    padding: 17px;
    box-shadow: 0 4px 15px rgba(25,70,48,0.045);
    height: 100%;
}

.card-title {
    font-size: 17px;
    font-weight: 800;
    color: #10261d;
    margin-bottom: 8px;
}

.card-label {
    font-size: 11px;
    font-weight: 750;
    color: #708078;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.muted {
    color: #738078;
}

/* ================= PRICE ================= */

.price-card {
    background: linear-gradient(135deg, #ffffff, #f7fcf9);
    border: 1px solid #dce8e2;
    border-radius: 16px;
    padding: 19px;
    box-shadow: 0 4px 16px rgba(22,75,48,0.05);
    height: 100%;
}

.price-main {
    font-size: 38px;
    font-weight: 850;
    color: #10261d;
}

.price-unit {
    font-size: 14px;
    color: #6d7973;
}

.live-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 17px;
    background: #e9f9f1;
    color: #087e4d;
    font-size: 10px;
    font-weight: 800;
    border: 1px solid #b8e8d1;
}

/* ================= AI ================= */

.ai-card {
    background: linear-gradient(135deg, #f5fbff, #f5fbf7);
    border: 1px solid #dbe9e2;
    border-radius: 16px;
    padding: 19px;
    height: 100%;
}

.ai-direction {
    font-size: 24px;
    font-weight: 850;
}

.ai-up {
    color: #078c4f;
}

.ai-down {
    color: #c33e3e;
}

.ai-stable {
    color: #a56b00;
}

 .weather-advisory {
    margin-top: 18px;
    padding: 18px 20px;
    border-radius: 14px;
    background: linear-gradient(135deg, #eefaf3, #f7fcf9);
    border: 1px solid #bfe4ce;
    border-left: 7px solid #087f4f;
    box-shadow: 0 5px 18px rgba(8,127,79,.08);
    font-size: 15px;
    line-height: 1.55;
}

.weather-advisory-title {
    font-size: 17px;
    font-weight: 850;
    letter-spacing: .1px;
}

.weather-advisory-reason {
    margin-top: 8px;
    color: #5f7168;
    font-size: 14px;
}

.confidence {
    float: right;
    border: 1px solid #9dcce7;
    background: #f0f9ff;
    color: #1973a5;
    padding: 5px 10px;
    border-radius: 18px;
    font-weight: 700;
    font-size: 11px;
}

.alert-box {
    border-radius: 10px;
    padding: 10px 12px;
    background: #f3f8fc;
    border-left: 4px solid #1689cf;
    margin-top: 9px;
    font-size: 12px;
}

.recommendation {
    border-radius: 10px;
    padding: 10px 12px;
    background: #fff8e9;
    border-left: 4px solid #f1b21c;
    margin-top: 9px;
    font-size: 12px;
}

/* ================= FORECAST ================= */

.forecast-box {
    background: white;
    border: 1px solid #e1e9e4;
    border-radius: 12px;
    padding: 10px 5px;
    text-align: center;
    min-height: 130px;
}

.forecast-day {
    font-size: 11px;
    font-weight: 800;
    color: #66756d;
}

.forecast-temp {
    font-size: 18px;
    font-weight: 800;
    color: #152820;
}

.forecast-rain {
    font-size: 10px;
    color: #607068;
}

/* ================= FOOTER ================= */

.footer {
    margin-top: 28px;
    padding: 23px 20px;
    border-radius: 16px 16px 0 0;
    background: linear-gradient(135deg, #064b34, #08734b);
    color: white;
    text-align: center;
}

.footer-brand {
    font-size: 20px;
    font-weight: 800;
}

.footer-text {
    color: rgba(255,255,255,0.78);
    font-size: 11px;
    margin-top: 4px;
}

.footer a {
    color: white !important;
    font-weight: 750;
    text-decoration: none;
}

/* ================= STREAMLIT ================= */

div.stButton > button {
    border-radius: 10px;
    border: none;
    background: #07874e;
    color: white;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #056d40;
    color: white;
}

.stSelectbox label {
    font-weight: 700;
    color: #33453d;
}

@media (max-width: 900px) {

    .navbar {
        flex-direction: column;
        align-items: flex-start;
    }

    .nav-wrap {
        justify-content: flex-start;
    }

    .nav-pill {
        margin: 2px;
    }

    .hero {
        height: auto;
        min-height: 230px;
        padding: 28px 25px;
    }

    .hero-title {
        font-size: 34px;
    }

    .hero-subtitle {
        font-size: 18px;
    }

    .hero-quote {
        position: static;
        margin-top: 20px;
        text-align: left;
        font-size: 13px;
    }
}

.system-health-kpi {
    margin-top: 24px;
    padding: 22px 26px;
    border-radius: 18px;
    border: 1px solid #cfe6d8;
    background: linear-gradient(135deg, #eefaf3, #f8fcfa);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    box-shadow: 0 8px 24px rgba(25,70,48,.07);
}

.system-health-kpi-bad {
    background: linear-gradient(135deg, #fff4f2, #fffafa);
    border-color: #f0c8c2;
}

.system-health-kpi-label {
    font-size: 12px;
    font-weight: 900;
    letter-spacing: .12em;
    color: #718078;
}

.system-health-kpi-title {
    margin-top: 4px;
    font-size: 22px;
    font-weight: 900;
    color: #12352a;
}

.system-health-kpi-message {
    margin-top: 5px;
    font-size: 14px;
    color: #68776f;
}

.system-health-kpi-checks {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 10px;
}

.system-health-kpi-checks span {
    padding: 9px 13px;
    border-radius: 999px;
    background: #ffffff;
    border: 1px solid #d8e9df;
    font-size: 13px;
    font-weight: 800;
    color: #31453c;
    white-space: nowrap;
}

@media (max-width: 900px) {
    .system-health-kpi {
        flex-direction: column;
        align-items: flex-start;
    }

    .system-health-kpi-checks {
        justify-content: flex-start;
    }
}


/* ================= MARKET KPI STRIP ================= */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 10px 0 16px 0;
}

.kpi-card {
    background: linear-gradient(180deg, #ffffff 0%, #fbfdfc 100%);
    border: 1px solid #e4ece7;
    border-radius: 12px;
    padding: 10px 13px;
    min-height: 78px;
    box-shadow: 0 2px 9px rgba(25,70,48,0.035);
    display: flex;
    align-items: center;
    gap: 10px;
}

.kpi-icon {
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    border-radius: 50%;
    background: #edf8f2;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.kpi-value {
    font-size: 22px;
    line-height: 1.05;
    font-weight: 850;
    color: #10261d;
}

.kpi-label {
    margin-top: 3px;
    color: #687870;
    font-size: 11px;
    line-height: 1.25;
}

@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

</style>
""".replace("__HERO_IMAGE__", HERO_IMAGE),
    unsafe_allow_html=True,
)


# ============================================================
# API HELPERS
# ============================================================

def api_get(endpoint, params=None, timeout=70):
    try:
        params = params or {}

        if endpoint == "/market-price":
            return get_mandi_prices(
                state=params.get("state"),
                district=params.get("district"),
                market=params.get("market"),
                commodity=params.get("commodity"),
                limit=int(params.get("limit", 100)),
                offset=int(params.get("offset", 0)),
            )

        if endpoint == "/model-status":
            return {
                "status": "loaded",
                "model": price_prediction_service.model_data["model_name"],
                "features": len(price_prediction_service.features),
            }

        return {
            "status": "error",
            "message": f"Unsupported backend endpoint: {endpoint}",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


def _government_mandi_page(
    state=None,
    district=None,
    market=None,
    commodity=None,
    limit=1000,
    offset=0,
):
    """Fetch one page from the same government mandi API used by the backend."""
    api_key = _mandi_service._get_api_key()
    if not api_key:
        raise ValueError("DATA_GOV_API_KEY is not configured in .env")

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

    response = requests.get(
        _mandi_service.API_URL,
        params=params,
        headers={"User-Agent": "Kissan-Seva/1.0"},
        timeout=(10, 60),
    )
    response.raise_for_status()
    return response.json()


def api_post(endpoint, payload, timeout=30):
    try:
        if endpoint == "/irrigation":
            return get_irrigation_recommendation(
                payload.get("weather", {})
            )

        if endpoint == "/predict":
            result = price_prediction_service.predict(payload)
            return {
                "status": "success",
                "prediction": result["prediction"],
                "confidence": result["confidence"],
            }

        return {
            "status": "error",
            "message": f"Unsupported backend endpoint: {endpoint}",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


# ============================================================
# MANDI DATA
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_mandi_records(limit=1000):
    """Compatibility wrapper.

    The dashboard intentionally does not download the complete India mandi
    dataset at startup. A state is selected first, then only that state's
    current records are requested.
    """
    return pd.DataFrame(), "Select a state to load current mandi data."


def _clean_mandi_dataframe(df):
    """Normalize government mandi records into the columns used by the UI."""
    df = df.copy()

    required_text_columns = [
        "state",
        "district",
        "market",
        "commodity",
        "variety",
        "grade",
        "arrival_date",
    ]

    for column in required_text_columns:
        if column not in df.columns:
            df[column] = ""

    for column in ["min_price", "max_price", "modal_price"]:
        if column not in df.columns:
            df[column] = np.nan
        df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in required_text_columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df.drop_duplicates().reset_index(drop=True)


def get_mandi_coverage_summary(state_df, selected_state):
    """Return simple coverage metrics for the currently loaded state."""
    if state_df is None or state_df.empty:
        return {
            "districts": 0,
            "markets": 0,
            "commodities": 0,
            "records": 0,
        }

    def unique_count(column):
        if column not in state_df.columns:
            return 0
        values = (
            state_df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        values = values[values != ""]
        values = values[values.str.casefold() != "nan"]
        return int(values.nunique())

    return {
        "districts": unique_count("district"),
        "markets": unique_count("market"),
        "commodities": unique_count("commodity"),
        "records": int(len(state_df)),
    }


@st.cache_data(ttl=300, show_spinner=False)
def load_state_mandi_records(state):
    """Load only the selected state's current mandi records.

    This is the important deployment fix: the app no longer requests the
    complete India dataset before the user selects a state. That prevents a
    large unfiltered data.gov.in request from breaking the entire dashboard.
