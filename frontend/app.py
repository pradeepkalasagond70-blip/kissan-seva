import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
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
from backend.karnataka_apmc_service import (
    load_karnataka_apmc_master,
    merge_karnataka_current_prices,
    KARNATAKA_MARKETS,
    canonical_district,
    normalize_market,
)

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

    /* ================= MOBILE GLOBAL ================= */

    .block-container {
        max-width: 100%;
        padding-left: 14px;
        padding-right: 14px;
        padding-top: 0.25rem;
        padding-bottom: 1.25rem;
    }

    .stApp {
        overflow-x: hidden;
    }

    /* ================= MOBILE NAVBAR ================= */

    .navbar {
        width: 100%;
        box-sizing: border-box;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        padding: 13px 14px 15px;
        gap: 11px;
        margin-bottom: 14px;
        border-radius: 0 0 18px 18px;
    }

    .brand {
        width: 100%;
        min-width: 0;
        gap: 9px;
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        flex: 0 0 42px;
        font-size: 22px;
    }

    .brand-name {
        font-size: 21px;
        line-height: 1.05;
    }

    .brand-tagline {
        font-size: 10px;
        line-height: 1.3;
        margin-top: 4px;
        white-space: normal;
    }

    .nav-wrap {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 6px;
        justify-content: stretch;
    }

    .nav-pill {
        display: block;
        width: 100%;
        box-sizing: border-box;
        margin: 0;
        padding: 10px 5px;
        border-radius: 10px;
        text-align: center;
        font-size: 12px;
        line-height: 1.2;
        white-space: nowrap;
    }

    /* ================= MOBILE HERO ================= */

    /*
       The desktop hero uses a fixed height and absolute quote.
       On mobile the hero becomes normal document flow.
       This keeps every text element visible and prevents overlap.
    */

    .hero {
        height: auto;
        min-height: 0;
        box-sizing: border-box;
        padding: 25px 20px 22px;
        border-radius: 18px;
        margin-bottom: 16px;
        background-position: center center;
    }

    .hero-badge {
        max-width: 100%;
        box-sizing: border-box;
        padding: 7px 11px;
        font-size: 9px;
        line-height: 1.25;
        letter-spacing: 0.45px;
        white-space: normal;
    }

    .hero-title {
        font-size: 34px;
        line-height: 1.05;
        margin-top: 17px;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 17px;
        line-height: 1.25;
        margin-bottom: 8px;
    }

    .hero-description {
        max-width: 100%;
        font-size: 13px;
        line-height: 1.5;
    }

    /*
       KEEP the creator credit.
       The complete quote + credit block moves into normal flow
       on mobile instead of sitting absolutely over the description.
    */

    .hero-quote {
        position: static;
        width: 100%;
        box-sizing: border-box;
        margin-top: 17px;
        padding-top: 13px;
        border-top: 1px solid rgba(255,255,255,0.30);
        text-align: left;
        font-size: 13px;
        line-height: 1.45;
    }

    .hero-quote > div {
        margin-top: 10px !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        font-style: normal !important;
        white-space: normal;
    }

    .hero-quote a {
        display: inline-block;
        margin-top: 2px;
    }

    /* ================= FEATURE CARDS ================= */

    .feature-card {
        min-height: 106px;
        box-sizing: border-box;
        padding: 14px 10px 12px;
        border-radius: 14px;
    }

    .feature-icon-clean {
        width: 40px;
        height: 40px;
        margin-bottom: 6px;
        font-size: 21px;
    }

    .feature-title {
        font-size: 12px;
        line-height: 1.3;
    }

    .feature-sub {
        font-size: 10px;
        line-height: 1.35;
        margin-top: 2px;
    }

    .feature-open {
        opacity: 1;
        font-size: 10px;
        margin-top: 6px;
    }

    /* ================= SECTION HEADINGS ================= */

    .section-title {
        font-size: 20px;
        line-height: 1.25;
        margin-top: 12px;
    }

    .section-description {
        font-size: 12px;
        line-height: 1.45;
    }

    /* ================= MARKET KPI ================= */

    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
        margin: 9px 0 14px;
    }

    .kpi-card {
        min-height: 76px;
        padding: 9px;
        gap: 8px;
    }

    .kpi-icon {
        width: 31px;
        height: 31px;
        flex: 0 0 31px;
        font-size: 14px;
    }

    .kpi-value {
        font-size: 19px;
    }

    .kpi-label {
        font-size: 10px;
    }

    /* ================= GENERAL CARDS ================= */

    .card,
    .price-card,
    .ai-card {
        width: 100%;
        box-sizing: border-box;
        padding: 15px;
        border-radius: 14px;
    }

    .card-title {
        font-size: 16px;
        line-height: 1.3;
    }

    .price-main {
        font-size: 31px;
        line-height: 1.1;
        word-break: normal;
    }

    .price-unit {
        font-size: 12px;
    }

    .ai-direction {
        font-size: 21px;
        line-height: 1.2;
    }

    .confidence {
        float: none;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    /* ================= WEATHER / IRRIGATION ================= */

    .weather-advisory {
        margin-top: 14px;
        padding: 14px;
        border-left-width: 5px;
    }

    .weather-advisory-title {
        font-size: 14px;
        line-height: 1.3;
    }

    .weather-advisory-reason {
        font-size: 12px;
        line-height: 1.5;
    }

    /* ================= 7-DAY FORECAST ================= */

    .forecast-box {
        min-height: 112px;
        padding: 8px 3px;
    }

    .forecast-day {
        font-size: 10px;
    }

    .forecast-temp {
        font-size: 16px;
    }

    .forecast-rain {
        font-size: 8px;
        line-height: 1.3;
    }

    /* ================= RESOURCE / ALERT CARDS ================= */

    .info-link-card .card {
        min-height: 165px;
        height: auto;
        padding: 16px 14px;
    }

    .info-link-card .card-title {
        font-size: 16px;
    }

    .info-link-card .card p {
        font-size: 11px;
        line-height: 1.45;
    }

    /* ================= SYSTEM HEALTH ================= */

    .system-health-kpi {
        flex-direction: column;
        align-items: flex-start;
        gap: 14px;
        padding: 17px;
    }

    .system-health-kpi-title {
        font-size: 19px;
    }

    .system-health-kpi-message {
        font-size: 12px;
        line-height: 1.45;
    }

    .system-health-kpi-checks {
        width: 100%;
        justify-content: flex-start;
        gap: 7px;
    }

    .system-health-kpi-checks span {
        font-size: 11px;
        padding: 7px 10px;
    }

    /* ================= FOOTER ================= */

    .footer {
        margin-top: 22px;
        padding: 20px 14px;
    }

    .footer-brand {
        font-size: 19px;
    }

    .footer-text {
        font-size: 10px;
    }
}

@media (max-width: 520px) {

    .block-container {
        padding-left: 10px;
        padding-right: 10px;
    }

    .navbar {
        padding-left: 11px;
        padding-right: 11px;
    }

    .hero {
        padding: 22px 17px 20px;
    }

    .hero-title {
        font-size: 31px;
    }

    .hero-subtitle {
        font-size: 16px;
    }

    .hero-description {
        font-size: 12.5px;
    }

    .hero-quote {
        font-size: 12.5px;
    }

    .hero-quote > div {
        font-size: 11.5px !important;
    }

    .kpi-grid {
        gap: 7px;
    }

    .kpi-card {
        padding: 8px;
    }

    .kpi-value {
        font-size: 17px;
    }

    .kpi-label {
        font-size: 9px;
    }

    .price-main {
        font-size: 28px;
    }

    .feature-card {
        min-height: 102px;
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
    """
    Load current mandi records.

    Karnataka is sourced from the SQLite-backed service.
    Other states continue to use the existing government API.
    """
    try:
        page_size = max(1, min(int(limit), 1000))
        all_records = []
        offset = 0
        total = None

        # Existing government API flow for non-Karnataka data.
        while True:
            page = _government_mandi_page(
                limit=page_size,
                offset=offset,
            )

            if not isinstance(page, dict):
                break

            records = page.get("records", [])
            page_total = int(page.get("total", 0) or 0)

            if total is None:
                total = page_total
            elif page_total > total:
                total = page_total

            if not records:
                break

            all_records.extend(records)
            offset += len(records)

            if total and offset >= total:
                break

            if len(records) < page_size:
                break

        # Karnataka comes from our local SQLite database.
        karnataka_result = get_mandi_prices(
            state="Karnataka",
            limit=1000,
            offset=0,
        )

        if (
            isinstance(karnataka_result, dict)
            and karnataka_result.get("status") == "success"
        ):
            all_records.extend(karnataka_result.get("records", []))

        if not all_records:
            return pd.DataFrame(), "No current mandi records returned."

        df = pd.DataFrame(all_records)

        required_columns = [
            "state",
            "district",
            "market",
            "commodity",
            "variety",
            "grade",
            "arrival_date",
        ]

        for column in required_columns:
            if column not in df.columns:
                df[column] = ""

        for column in ["min_price", "max_price", "modal_price"]:
            if column not in df.columns:
                df[column] = np.nan

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        for column in required_columns:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        df = df.drop_duplicates().reset_index(drop=True)

        return df, None

    except Exception as exc:
        return pd.DataFrame(), str(exc)


@st.cache_data(ttl=300, show_spinner=False)
def load_state_mandi_records(state):
    """
    Load records for the selected state.

    Karnataka -> SQLite-backed service.
    Other states -> existing government API dataset.
    """
    try:
        wanted_state = str(state).strip().casefold()

        if wanted_state == "karnataka":
            result = get_mandi_prices(
                state="Karnataka",
                limit=1000,
                offset=0,
            )

            if not isinstance(result, dict):
                return pd.DataFrame(), "Invalid Karnataka mandi response."

            if result.get("status") != "success":
                return pd.DataFrame(), result.get(
                    "message",
                    "Unable to load Karnataka mandi data.",
                )

            records = result.get("records", [])

            if not records:
                return pd.DataFrame(), (
                    "No Karnataka mandi records are currently stored."
                )

            state_df = pd.DataFrame(records)

        else:
            # Preserve existing behavior for other states.
            all_df, error = load_mandi_records(1000)

            if error:
                return pd.DataFrame(), error

            if all_df.empty:
                return pd.DataFrame(), "No current mandi records returned."

            state_df = all_df[
                all_df["state"].astype(str).str.strip().str.casefold()
                == wanted_state
            ].copy()

        if state_df.empty:
            return pd.DataFrame(), (
                f"No current mandi records returned for {state}."
            )

        if wanted_state == "karnataka" and "district" in state_df.columns:
            state_df["district"] = state_df["district"].map(
                canonical_district
            )

        return state_df.reset_index(drop=True), None

    except Exception as exc:
        return pd.DataFrame(), str(exc)


# ============================================================
# KARNATAKA APMC MASTER
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_karnataka_master():
    """Load the local Karnataka district/APMC master instantly.

    No ReMS network call is made here. The service contains the local
    geography master and this function has a second in-code fallback so the
    Karnataka selector never becomes dependent on a remote website.
    """
    try:
        master = load_karnataka_apmc_master()
        if master is not None and not master.empty:
            return master.copy()
    except Exception:
        pass

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
    ).drop_duplicates(["district", "market"]).reset_index(drop=True)


@st.cache_data(ttl=300, show_spinner=False)
def build_state_selection_df(state, current_df):
    """Return current prices plus Karnataka's complete market master."""
    if str(state).strip().casefold() != "karnataka":
        return current_df.copy()

    master_df = load_karnataka_master()
    if master_df.empty:
        return current_df.copy()

    return merge_karnataka_current_prices(master_df, current_df)


@st.cache_data(ttl=300, show_spinner=False)
def load_karnataka_recent_price_history(
    district,
    market,
    commodity,
    days=7,
):
    """
    Find the newest Karnataka price observation available in SQLite.

    The actual arrival_date is retained, so older prices are never labelled
    as today's price.
    """
    try:
        result = get_mandi_prices(
            state="Karnataka",
            district=district,
            market=market,
            commodity=commodity,
            limit=1000,
            offset=0,
        )

        if not isinstance(result, dict):
            return pd.DataFrame()

        if result.get("status") != "success":
            return pd.DataFrame()

        records = result.get("records", [])

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        if "arrival_date" not in df.columns:
            return pd.DataFrame()

        df["arrival_date"] = pd.to_datetime(
            df["arrival_date"],
            errors="coerce",
            dayfirst=True,
        )

        today = pd.Timestamp.today().normalize()
        cutoff = today - pd.Timedelta(days=max(0, int(days) - 1))

        df = df[
            df["arrival_date"].notna()
            & (df["arrival_date"] >= cutoff)
            & (df["arrival_date"] <= today)
        ].copy()

        for column in ["min_price", "max_price", "modal_price"]:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )

        return df.sort_values(
            "arrival_date",
            ascending=False,
        ).reset_index(drop=True)

    except Exception:
        return pd.DataFrame()


# ============================================================
# MANDI DATA COVERAGE SUMMARY
# ============================================================

def get_mandi_coverage_summary(df, state):
    """Return district/APMC/commodity counts for the selected state."""
    if df is None or df.empty:
        return {
            "districts": 0,
            "markets": 0,
            "commodities": 0,
            "records": 0,
        }

    state_df = df[
        df["state"].astype(str).str.strip().str.casefold()
        == str(state).strip().casefold()
    ]

    return {
        "districts": int(state_df["district"].replace("", pd.NA).dropna().nunique()),
        "markets": int(state_df["market"].replace("", pd.NA).dropna().nunique()),
        "commodities": int(state_df["commodity"].replace("", pd.NA).dropna().nunique()),
        "records": int(len(state_df)),
    }


# ============================================================
# WEATHER
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def geocode_location(location, state=None):
    queries = []

    if state:
        queries.append(f"{location}, {state}, India")

    queries.append(f"{location}, India")
    if state:
        queries.append(f"{state}, India")

    for query in queries:
        try:
            response = requests.get(
                GEOCODING_URL,
                params={
                    "name": query,
                    "count": 10,
                    "language": "en",
                    "format": "json",
                },
                headers={"User-Agent": "Kissan-Seva/1.0"},
                timeout=15,
            )
            response.raise_for_status()

            results = response.json().get("results", [])

            if not results:
                continue

            # Prefer India and, when possible, the requested state.
            india_results = [
                item for item in results
                if str(item.get("country_code", "")).upper() == "IN"
            ]

            candidates = india_results or results

            if state:
                state_lower = state.lower()
                state_matches = [
                    item for item in candidates
                    if state_lower in str(item.get("admin1", "")).lower()
                    or state_lower in str(item.get("admin2", "")).lower()
                ]
                if state_matches:
                    candidates = state_matches

            result = candidates[0]

            return {
                "name": result.get("name"),
                "country": result.get("country"),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
            }

        except Exception:
            continue

    return None


@st.cache_data(ttl=1800, show_spinner=False)
def get_weather(latitude, longitude):
    base_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "wind_speed_10m",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum",
            "et0_fao_evapotranspiration",
        ]),
        "forecast_days": 7,
        "timezone": "auto",
    }

    # First try the complete weather payload.
    try:
        response = requests.get(
            WEATHER_URL,
            params=base_params,
            headers={"User-Agent": "Kissan-Seva/1.0"},
            timeout=25,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        pass

    # Fallback: request weather without ET0. This keeps the weather
    # dashboard alive even if one optional forecast variable fails.
    fallback_params = dict(base_params)
    fallback_params["daily"] = ",".join([
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
        "precipitation_sum",
    ])

    try:
        response = requests.get(
            WEATHER_URL,
            params=fallback_params,
            headers={"User-Agent": "Kissan-Seva/1.0"},
            timeout=25,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


# ============================================================
# NAVBAR
# ============================================================

html(
    """
<div class="navbar">
    <div class="brand">
        <div class="brand-icon">🌿</div>
        <div>
            <div class="brand-name">Kissan Seva</div>
            <div class="brand-tagline">
                Smarter Farming. Brighter Tomorrow.
            </div>
        </div>
    </div>

    <div class="nav-wrap">
        <a class="nav-pill active" href="#top">⌂ Home</a>
        <a class="nav-pill" href="#market-section">▥ Market Prices</a>
        <a class="nav-pill" href="#weather-section">☁ Weather</a>
        <a class="nav-pill" href="#ai-section">✦ AI Insights</a>
        <a class="nav-pill" href="#resources-section">▣ Resources</a>
        <a class="nav-pill" href="#about-section">ⓘ About</a>
    </div>
</div>
"""
)


# ============================================================
# HERO
# ============================================================

html(
    """
    <div class="hero" id="top">
        <div class="hero-badge">
            🌾 AI-POWERED FARMING INTELLIGENCE
        </div>

        <div class="hero-title">
            Kissan Seva
        </div>

        <div class="hero-subtitle">
            Real Data. Real Insights. Real Impact.
        </div>

        <div class="hero-description">
            Government mandi prices, weather forecasts and
            AI-powered market insights to help farmers make
            smarter decisions.
        </div>

        <div class="hero-quote">
            “Better Information<br>
            A Stronger Tomorrow” 🌿
            <div style="margin-top:14px;font-size:16px;font-style:normal;line-height:1.35;">
                Built by <b>Pradeep Kalasagond</b>
                <span style="margin:0 5px;">·</span>
                <a href="https://www.linkedin.com/in/pradeep-kalasagond-95579a230"
                   target="_blank"
                   style="color:white !important;text-decoration:none;font-weight:750;">
                    LinkedIn ↗
                </a>
            </div>
        </div>
    </div>
    """
)


# ============================================================
# FEATURE STRIP — CLICKABLE NAVIGATION
# ============================================================

features = [
    ("₹", "Current Mandi Prices", "Government market data", "#market-section"),
    ("☁", "Weather Forecasts", "7-day weather insights", "#weather-section"),
    ("🔮", "AI Price Predictions", "Data-driven market outlook", "#ai-section"),
    ("💧", "Irrigation Advisory", "Weather-based decisions", "#irrigation-section"),
]

feature_cols = st.columns(4)

for col, feature in zip(feature_cols, features):
    with col:
        html(
            f"""
            <a class="feature-link" href="{feature[3]}">
                <div class="feature-card">
                    <div class="feature-icon feature-icon-clean">{feature[0]}</div>
                    <div class="feature-title">{feature[1]}</div>
                    <div class="feature-sub">{feature[2]}</div>
                    <div class="feature-open">View details →</div>
                </div>
            </a>
            """
        )


# ============================================================
# MARKET SECTION
# ============================================================

st.markdown('<div id="market-section"></div>', unsafe_allow_html=True)
html(
    """
    <div class="section-title">
        🔎 Check Market Price & Get AI Insights
    </div>
    <div class="section-description">
        Select a location and market that is currently available
        in the government mandi data.
    </div>
    """
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading complete current mandi data..."):
    mandi_df, mandi_error = load_mandi_records(1000)

if mandi_error:
    st.error("Unable to load government mandi data right now.")
    st.caption(mandi_error)
    st.stop()

if mandi_df.empty:
    st.warning("No mandi data is currently available.")
    st.stop()


# ============================================================
# DEPENDENT FILTERS
# State -> District -> Commodity -> Market
# ============================================================

states = sorted(
    [
        value
        for value in mandi_df["state"].unique()
        if value and str(value).lower() != "nan"
    ]
)

if "Karnataka" not in states:
    states.append("Karnataka")
    states = sorted(states)

state_col, district_col, commodity_col, market_col = st.columns(4)

with state_col:
    default_state_index = states.index("Karnataka") if "Karnataka" in states else 0
    selected_state = st.selectbox(
        "State",
        states,
        index=default_state_index,
        key="kissan_state",
    )

with st.spinner(f"Loading {selected_state} mandi data..."):
    state_current_df, state_error = load_state_mandi_records(selected_state)

is_karnataka = str(selected_state).strip().casefold() == "karnataka"

# ============================================================
# CURRENT PRICE SELECTION
# ============================================================

# For Karnataka:
#   - Districts come from the complete Karnataka APMC master.
#   - Commodities come ONLY from actual government records
#     for the selected district.
#   - Markets come ONLY from actual government records
#     for the selected district + commodity.
#
# For all other states:
#   - Existing government-feed behavior remains unchanged.
#
# IMPORTANT:
# The Karnataka APMC master is used only for district visibility.
# It does NOT manufacture commodity or price data.

current_feed_df = state_current_df.copy()

# Karnataka gets the complete district geography from the APMC master.
# Other states continue using their current government-feed records.
state_df = build_state_selection_df(
    selected_state,
    current_feed_df,
)

# ------------------------------------------------------------
# DISTRICTS
# ------------------------------------------------------------

districts = sorted([
    str(x).strip()
    for x in state_df.get(
        "district",
        pd.Series(dtype=str)
    ).dropna().astype(str).unique()
    if str(x).strip()
    and str(x).casefold() != "nan"
])

# ------------------------------------------------------------
# CURRENT GOVERNMENT-FEED COVERAGE
# ------------------------------------------------------------

# Coverage cards must represent actual government reporting,
# not the Karnataka master list.
coverage = get_mandi_coverage_summary(
    current_feed_df,
    selected_state
)

html(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon">📍</div>
            <div>
                <div class="kpi-value">{coverage["districts"]}</div>
                <div class="kpi-label">Districts reporting</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏪</div>
            <div>
                <div class="kpi-value">{coverage["markets"]}</div>
                <div class="kpi-label">APMCs / Markets</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🌾</div>
            <div>
                <div class="kpi-value">{coverage["commodities"]}</div>
                <div class="kpi-label">Current commodities</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📊</div>
            <div>
                <div class="kpi-value">{coverage["records"]:,}</div>
                <div class="kpi-label">Current price records</div>
            </div>
        </div>
    </div>
    """
)

if not districts:
    st.warning(f"No district information is available for {selected_state}.")
    st.stop()

# ------------------------------------------------------------
# DISTRICT SELECTOR
# ------------------------------------------------------------

with district_col:
    selected_district = st.selectbox(
        "District",
        districts,
        key=f"kissan_district_{selected_state}",
    )

# ------------------------------------------------------------
# SELECTED DISTRICT DATA
# ------------------------------------------------------------

# For Karnataka, state_df may contain master-only rows.
# For commodities we must use actual current government records,
# so filter current_feed_df rather than the master-augmented state_df.
if is_karnataka:
    district_df = current_feed_df[
        current_feed_df.get(
            "district",
            pd.Series(dtype=str)
        ).astype(str).str.casefold()
        == selected_district.casefold()
    ].copy()
else:
    district_df = state_df[
        state_df.get(
            "district",
            pd.Series(dtype=str)
        ).astype(str).str.casefold()
        == selected_district.casefold()
    ].copy()

# ------------------------------------------------------------
# COMMODITIES
# ------------------------------------------------------------

# Commodity options come ONLY from actual government records
# for the selected district.
commodities = sorted({
    x.strip()
    for x in district_df.get(
        "commodity",
        pd.Series(dtype=str)
    ).dropna().astype(str).unique()
    if x.strip()
    and x.casefold() != "nan"
})

if not commodities:
    st.warning(
        f"No current commodity data is available for {selected_district}."
    )
    if is_karnataka:
        st.info(
            "This district exists in the Karnataka APMC master, "
            "but the current government feed has no commodity record "
            "for this district."
        )
    st.stop()

with commodity_col:
    selected_commodity = st.selectbox(
        "Commodity",
        commodities,
        key=(
            f"kissan_commodity_"
            f"{selected_state}_"
            f"{selected_district}"
        ),
    )

# ------------------------------------------------------------
# SELECTED COMMODITY DATA
# ------------------------------------------------------------

commodity_df = district_df[
    district_df.get(
        "commodity",
        pd.Series(dtype=str)
    ).astype(str).str.casefold()
    == selected_commodity.casefold()
].copy()

# ------------------------------------------------------------
# MARKETS
# ------------------------------------------------------------

if not commodity_df.empty and "market" in commodity_df.columns:
    commodity_df["market_key"] = (
        commodity_df["market"].map(normalize_market)
    )

# Markets come ONLY from actual government records
# for the selected district + commodity.
markets = sorted({
    x.strip()
    for x in commodity_df.get(
        "market",
        pd.Series(dtype=str)
    ).dropna().astype(str).unique()
    if x.strip()
    and x.casefold() != "nan"
})

if not markets:
    st.warning(
        "No APMC / market is available for this district and commodity yet."
    )
    st.stop()

with market_col:
    selected_market = st.selectbox(
        "Market",
        markets,
        key=(
            f"kissan_market_"
            f"{selected_state}_"
            f"{selected_district}_"
            f"{selected_commodity}"
        ),
    )

# ============================================================
# FINAL SELECTION
# ============================================================

if not commodity_df.empty and "market_key" in commodity_df.columns:
    selected_market_key = normalize_market(selected_market)
    selected_df = commodity_df[
        commodity_df["market_key"] == selected_market_key
    ].copy()
else:
    selected_df = commodity_df[
        commodity_df["market"] == selected_market
    ].copy()

if selected_df.empty and is_karnataka:
    selected_df = pd.DataFrame([{
        "state": "Karnataka",
        "district": selected_district,
        "market": selected_market,
        "commodity": selected_commodity,
        "variety": "",
        "grade": "",
        "min_price": np.nan,
        "max_price": np.nan,
        "modal_price": np.nan,
        "arrival_date": pd.NaT,
    }])

if selected_df.empty:
    st.warning("No records are available for this selection.")
    st.stop()

# If today's/current feed has no price for Karnataka, search up to seven days
# back and use the newest real observation. Never label an older price as today.
if is_karnataka and not selected_df["modal_price"].notna().any():
    fallback_df = load_karnataka_recent_price_history(
        selected_district, selected_market, selected_commodity, days=7
    )
    if not fallback_df.empty:
        selected_df = fallback_df.copy()

selected_df = selected_df.drop(columns=["market_key"], errors="ignore")

selected_df["modal_price"] = pd.to_numeric(
    selected_df["modal_price"],
    errors="coerce",
)

selected_df["min_price"] = pd.to_numeric(
    selected_df["min_price"],
    errors="coerce",
)

selected_df["max_price"] = pd.to_numeric(
    selected_df["max_price"],
    errors="coerce",
)

price_available = selected_df["modal_price"].notna().any()

selected_df["arrival_date"] = pd.to_datetime(
    selected_df["arrival_date"],
    errors="coerce",
    dayfirst=True,
)

selected_df = selected_df.sort_values(
    "arrival_date", na_position="last"
)

if price_available:
    priced_df = selected_df.dropna(subset=["modal_price"]).copy()
    latest = priced_df.iloc[-1]
    modal_price = float(latest["modal_price"])
    min_price = (
        float(latest["min_price"])
        if pd.notna(latest["min_price"])
        else modal_price
    )
    max_price = (
        float(latest["max_price"])
        if pd.notna(latest["max_price"])
        else modal_price
    )
else:
    modal_price = None
    min_price = None
    max_price = None

price_date_label = ""
price_freshness_label = "No price in the last 7 days"
if price_available:
    latest_date = latest.get("arrival_date")
    if pd.notna(latest_date):
        latest_date = pd.Timestamp(latest_date)
        age_days = max(0, (pd.Timestamp.today().normalize() - latest_date.normalize()).days)
        price_date_label = latest_date.strftime("%d %b %Y")
        price_freshness_label = "Latest reported price" if age_days == 0 else f"Latest available • {age_days} day(s) old"


# ============================================================
# PRICE + MARKET INFO
# ============================================================

price_col, info_col = st.columns([2.4, 1.1])

with price_col:
    html(
        f"""
        <div class="price-card">
            <span class="live-badge">
                ✦ GOVERNMENT DATA
            </span>

            <div style="margin-top:10px;" class="card-title">
                ₹ Current Market Price
            </div>

            <div style="font-size:13px;color:#6d7973;">
                {selected_commodity} |
                {selected_market} |
                {selected_district}, {selected_state}
            </div>

            <div style="margin-top:12px;" class="price-main">
                {"₹ " + format(modal_price, ",.0f") if modal_price is not None else "No current price reported"}
                {"<span class='price-unit'>/ Quintal</span>" if modal_price is not None else ""}
            </div>

            <div style="margin-top:8px;font-size:12px;color:#687870;">
                {price_freshness_label}{" • " + price_date_label if price_date_label else ""}
            </div>

            <div style="margin-top:12px;font-size:13px;">
                {"<b>Minimum:</b> ₹ " + format(min_price, ",.0f") + "&nbsp;&nbsp;&nbsp;<b>Maximum:</b> ₹ " + format(max_price, ",.0f") if modal_price is not None else "This APMC is in the official market master, but no price was found in the latest 7-day government window."}
            </div>
        </div>
        """
    )

with info_col:
    html(
        f"""
        <div class="card">
            <div class="card-title">📍 Market Information</div>

            <div class="card-label">State</div>
            <div style="font-weight:700;">{selected_state}</div>

            <br>

            <div class="card-label">District</div>
            <div style="font-weight:700;">{selected_district}</div>

            <br>

            <div class="card-label">Market</div>
            <div style="font-weight:700;">{selected_market}</div>
        </div>
        """
    )


# ============================================================
# TABLE
# ============================================================

html(
    """
    <br>
    <div class="card-title">
        📋 Current Mandi Records
    </div>
    """
)

display_columns = [
    "state",
    "district",
    "market",
    "commodity",
    "variety",
    "grade",
    "min_price",
    "max_price",
    "modal_price",
    "arrival_date",
]

display_columns = [
    column
    for column in display_columns
    if column in selected_df.columns
]

display_df = selected_df[display_columns].copy()

display_df = display_df.rename(
    columns={
        "state": "State",
        "district": "District",
        "market": "Market",
        "commodity": "Commodity",
        "variety": "Variety",
        "grade": "Grade",
        "min_price": "Min Price",
        "max_price": "Max Price",
        "modal_price": "Modal Price",
        "arrival_date": "Date",
    }
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)


# ============================================================
# WEATHER + AI
# ============================================================

weather_location = geocode_location(selected_district)

weather_data = None

if weather_location:
    weather_data = get_weather(
        weather_location["latitude"],
        weather_location["longitude"],
    )

# Reuse one irrigation decision in both the weather card and advisory section.
irrigation_result = None
if weather_data:
    irrigation_result = api_post(
        "/irrigation",
        {"weather": weather_data},
    )

st.markdown('<div id="weather-section"></div>', unsafe_allow_html=True)
st.markdown('<div id="ai-section"></div>', unsafe_allow_html=True)
weather_col, ai_col = st.columns(2)


# ============================================================
# WEATHER CARD
# ============================================================

with weather_col:

    if weather_data:

        current = weather_data.get("current", {})

        temperature = current.get(
            "temperature_2m",
            0,
        )

        humidity = current.get(
            "relative_humidity_2m",
            0,
        )

        wind = current.get(
            "wind_speed_10m",
            0,
        )

        rainfall = current.get(
            "rain",
            0,
        )

        daily_preview = weather_data.get("daily", {})
        rain_probs = daily_preview.get("precipitation_probability_max", [])
        rain_sums = daily_preview.get("precipitation_sum", [])

        tomorrow_rain_prob = rain_probs[1] if len(rain_probs) > 1 else None
        tomorrow_rain = rain_sums[1] if len(rain_sums) > 1 else None

        farmer_decision = "CHECK SOIL MOISTURE"
        farmer_reason = (
            "Use soil moisture and field conditions before deciding to irrigate."
        )

        if irrigation_result and irrigation_result.get("status") == "success":
            farmer_decision = irrigation_result.get("recommendation", farmer_decision)
            farmer_reason = irrigation_result.get("reason", farmer_reason)
        elif tomorrow_rain_prob is not None and tomorrow_rain is not None:
            if tomorrow_rain_prob >= 60 and tomorrow_rain >= 5:
                farmer_decision = "IRRIGATION NOT REQUIRED"
                farmer_reason = (
                    f"Tomorrow: {tomorrow_rain_prob}% rain chance and "
                    f"{tomorrow_rain:.1f} mm expected. Consider skipping irrigation."
                )
            elif tomorrow_rain_prob >= 40 and tomorrow_rain >= 2:
                farmer_decision = "IRRIGATION MAY BE REQUIRED"
                farmer_reason = (
                    f"Tomorrow: {tomorrow_rain_prob}% rain chance and "
                    f"{tomorrow_rain:.1f} mm expected. Recheck soil moisture."
                )
            else:
                farmer_decision = "IRRIGATION MAY BE REQUIRED"
                farmer_reason = (
                    f"Tomorrow: only {tomorrow_rain:.1f} mm rain is expected. "
                    "Check soil moisture before watering."
                )

        decision_color = "#087f4f" if "NOT REQUIRED" in farmer_decision else "#a56b00"

        html(
            f"""
            <div class="card">
                <div class="card-title">
                    ☁️ Weather in {selected_district}
                </div>

                <div style="font-size:38px;font-weight:850;margin-top:8px;">
                    ☁️ {temperature:.1f}°C
                </div>

                <div style="margin-top:8px;font-size:13px;">
                    💧 Humidity: <b>{humidity}%</b>
                    &nbsp;&nbsp;
                    💨 Wind: <b>{wind} km/h</b>
                    &nbsp;&nbsp;
                    🌧️ Rain: <b>{rainfall} mm</b>
                </div>

                <div class="weather-advisory">
                    <div class="weather-advisory-title"
                         style="color:{decision_color};">
                        💧 Tomorrow's Irrigation Decision
                    </div>
                    <div style="font-size:20px;font-weight:900;color:{decision_color};margin-top:3px;">
                        {farmer_decision}
                    </div>
                    <div class="weather-advisory-reason">
                        {farmer_reason}
                    </div>
                </div>
            </div>
            """
        )


    else:

        html(
            f"""
            <div class="card">
                <div class="card-title">
                    ☁️ Weather
                </div>
                <div class="muted">
                    Weather data is temporarily unavailable for
                    {selected_district}.
                </div>
            </div>
            """
        )


# ============================================================
# AI MARKET OUTLOOK
# ============================================================

with ai_col:

    prediction_payload = {
        "lag_1": modal_price,
        "lag_2": modal_price,
        "lag_3": modal_price,
        "return_1d": 0.0,
        "return_2d": 0.0,
        "return_3d": 0.0,
        "ma_3": modal_price,
        "ma_7": modal_price,
        "volatility_7d": 0.0,
        "min_price": min_price,
        "max_price": max_price,
        "modal_price": modal_price,
        "day_of_week": datetime.now().weekday(),
        "month": datetime.now().month,
        "observations": len(selected_df),
    }

    prediction_result = api_post(
        "/predict",
        prediction_payload,
    )

    if prediction_result.get("status") == "success":

        prediction = prediction_result.get(
            "prediction",
            "STABLE",
        )

        confidence = prediction_result.get(
            "confidence"
        )

        if prediction == "UP":
            direction_class = "ai-up"
            icon = "↑"
            description = (
                "Price movement is likely to be upward."
            )
        elif prediction == "DOWN":
            direction_class = "ai-down"
            icon = "↓"
            description = (
                "Price movement is likely to be downward."
            )
        else:
            direction_class = "ai-stable"
            icon = "→"
            description = (
                "Price movement is likely to remain relatively stable."
            )

        confidence_text = (
            f"{confidence:.1f}%"
            if confidence is not None
            else "N/A"
        )

        html(
            f"""
            <div class="ai-card">
                <div class="card-title">
                    🧠 AI Market Outlook
                </div>

                <span class="confidence">
                    {confidence_text} Confidence
                </span>

                <div style="font-size:43px;font-weight:850;margin-top:8px;"
                     class="{direction_class}">
                    {icon}
                </div>

                <div class="ai-direction {direction_class}">
                    Price Likely to Go {prediction}
                </div>

                <div class="muted">
                    {description}
                </div>

                <div class="alert-box">
                    <b>📈 AI Insight</b><br>
                    The Random Forest model generated a directional
                    market outlook from the supplied market features.
                </div>

                <div class="recommendation">
                    <b>💡 Decision Support</b><br>
                    Use the AI outlook together with current mandi
                    prices, weather conditions and your own selling
                    requirements.
                </div>
            </div>
            """
        )

    else:

        html(
            """
            <div class="ai-card">
                <div class="card-title">
                    🧠 AI Market Outlook
                </div>
                <div class="muted">
                    AI prediction is temporarily unavailable.
                </div>
            </div>
            """
        )


# ============================================================
# IRRIGATION
# ============================================================

st.markdown('<div id="irrigation-section"></div>', unsafe_allow_html=True)

html(
    """
    <br>
    <div class="card-title">
        💧 Irrigation Advisory
    </div>
    """
)

if weather_data:

    if irrigation_result and irrigation_result.get("status") == "success":

        recommendation = irrigation_result.get(
            "recommendation",
            "UNAVAILABLE",
        )

        reason = irrigation_result.get(
            "reason",
            "",
        )

        if recommendation == "IRRIGATION NOT REQUIRED":
            st.success(f"💧 {recommendation}")
        elif recommendation == "IRRIGATION REQUIRED":
            st.error(f"💧 {recommendation}")
        else:
            st.warning(f"💧 {recommendation}")

        st.info(reason)

    else:
        st.warning(
            "Irrigation recommendation is temporarily unavailable."
        )

else:
    st.info(
        "Weather data is required for the irrigation advisory."
    )


# ============================================================
# 7-DAY FORECAST
# ============================================================

if weather_data:

    daily = weather_data.get(
        "daily",
        {},
    )

    dates = daily.get(
        "time",
        [],
    )

    max_temp = daily.get(
        "temperature_2m_max",
        [],
    )

    rain_probability = daily.get(
        "precipitation_probability_max",
        [],
    )

    rainfall = daily.get(
        "precipitation_sum",
        [],
    )

    html(
        """
        <br>
        <div class="card-title">
            ☁️ 7-Day Weather Forecast
        </div>
        """
    )

    forecast_cols = st.columns(7)

    for i, col in enumerate(forecast_cols):

        if i >= len(dates):
            continue

        date_obj = pd.to_datetime(dates[i])

        rain_value = (
            rainfall[i]
            if i < len(rainfall)
            else 0
        )

        rain_prob = (
            rain_probability[i]
            if i < len(rain_probability)
            else 0
        )

        temp_value = (
            max_temp[i]
            if i < len(max_temp)
            else 0
        )

        with col:

            html(
                f"""
                <div class="forecast-box">
                    <div class="forecast-day">
                        {date_obj.strftime("%a")}
                    </div>

                    <div style="font-size:10px;color:#7a8580;">
                        {date_obj.strftime("%d %b")}
                    </div>

                    <div style="font-size:23px;margin:6px 0;">
                        {"🌧️" if rain_value > 2 else "☀️"}
                    </div>

                    <div class="forecast-temp">
                        {temp_value:.0f}°C
                    </div>

                    <div class="forecast-rain">
                        🌧️ {rain_value:.1f} mm
                    </div>

                    <div class="forecast-rain">
                        {rain_prob}% rain chance
                    </div>
                </div>
                """
            )


# ============================================================
# MARKET ANALYSIS + PRICE TREND
# ============================================================

analysis_col, chart_col = st.columns([1.1, 1.9])

with analysis_col:

    average_price = selected_df["modal_price"].mean()
    highest_price = selected_df["modal_price"].max()
    lowest_price = selected_df["modal_price"].min()

    if len(selected_df) >= 2:

        first_price = float(
            selected_df.iloc[0]["modal_price"]
        )

        last_price = float(
            selected_df.iloc[-1]["modal_price"]
        )

        if first_price > 0:
            movement = (
                (last_price - first_price)
                / first_price
                * 100
            )
        else:
            movement = 0

    else:
        movement = 0

    if movement > 2:
        trend = "Upward ↑"
    elif movement < -2:
        trend = "Downward ↓"
    else:
        trend = "Stable →"

    html(
        f"""
        <div class="card">
            <div class="card-title">
                ₹ Market Analysis
            </div>

            <div style="display:flex;justify-content:space-between;padding:7px 0;">
                <span>Average Price</span>
                <b>₹ {average_price:,.0f}</b>
            </div>

            <div style="display:flex;justify-content:space-between;padding:7px 0;">
                <span>Highest Price</span>
                <b>₹ {highest_price:,.0f}</b>
            </div>

            <div style="display:flex;justify-content:space-between;padding:7px 0;">
                <span>Lowest Price</span>
                <b>₹ {lowest_price:,.0f}</b>
            </div>

            <div style="display:flex;justify-content:space-between;padding:7px 0;">
                <span>Observed Records</span>
                <b>{len(selected_df)}</b>
            </div>

            <div style="display:flex;justify-content:space-between;padding:7px 0;">
                <span>Observed Trend</span>
                <b style="color:#078c4f;">{trend}</b>
            </div>
        </div>
        """
    )


with chart_col:

    html(
        """
        <div class="card">
            <div class="card-title">
                📈 Price Trend
            </div>
        </div>
        """
    )

    chart_df = selected_df.copy()

    if len(chart_df) > 1:

        chart_df = chart_df.dropna(
            subset=["arrival_date"]
        )

        if not chart_df.empty:

            chart_df = (
                chart_df[
                    ["arrival_date", "modal_price"]
                ]
                .drop_duplicates(
                    subset=["arrival_date"]
                )
                .set_index("arrival_date")
                .tail(30)
            )

            if not chart_df.empty:
                st.line_chart(
                    chart_df,
                    width="stretch",
                )

            else:
                st.info(
                    "More dated observations are required "
                    "to display a trend."
                )

        else:
            st.info(
                "Date information is unavailable for the trend."
            )

    else:
        st.info(
            "More observations are required to display a trend."
        )


# ============================================================
# RESOURCES / ALERTS
# ============================================================

st.markdown('<div id="resources-section"></div>', unsafe_allow_html=True)

# Fetch the three health checks once.  The dashboard uses these values
# only for the single System Alerts / System Health KPI below.
weather_ok = bool(
    weather_data
    and weather_data.get("current")
    and weather_data.get("daily")
)

model_status = api_get(
    "/model-status",
    timeout=10,
)
model_ok = model_status.get("status") == "loaded"
mandi_ok = not bool(mandi_error) and not mandi_df.empty

health_checks = {
    "Mandi data": mandi_ok,
    "Weather service": weather_ok,
    "AI model": model_ok,
}

failed_services = [
    name for name, ok in health_checks.items() if not ok
]
all_systems_ok = len(failed_services) == 0

if all_systems_ok:
    health_icon = "🟢"
    health_title = "All Systems Operational"
    health_message = (
        "Mandi data, weather service and AI model are available."
    )
    health_class = "system-health-good"
else:
    health_icon = "🔴"
    health_title = "System Attention Required"
    health_message = (
        "Unavailable: " + ", ".join(failed_services) + "."
    )
    health_class = "system-health-bad"

quick_col, resource_col, alert_col = st.columns(3)

with quick_col:
    html(
        """
        <a class="info-link-card" href="https://kisansuvidha.gov.in/" target="_blank" rel="noopener noreferrer">
            <div class="card">
                <div class="info-link-icon">🔗</div>
                <div class="card-title">Quick Links</div>
                <p class="resource-list">🏛️ Government Schemes</p>
                <p class="resource-list">🌱 Farming Tips</p>
                <p class="resource-list">📅 Crop Calendar</p>
                <div class="card-action">Open Kisan Suvidha ↗</div>
            </div>
        </a>
        """
    )

with resource_col:
    html(
        """
        <a class="info-link-card" href="https://pmkisan.gov.in/" target="_blank" rel="noopener noreferrer">
            <div class="card">
                <div class="info-link-icon">📚</div>
                <div class="card-title">Farming Resources</div>
                <p class="resource-description">
                    Access official government farmer schemes, financial-support information,
                    eligibility details, and useful agricultural services.
                </p>
                <div class="card-action">Open PM-KISAN Portal ↗</div>
            </div>
        </a>
        """
    )

with alert_col:
    html(
        f"""
        <a class="info-link-card" href="#system-status-section">
            <div class="card {health_class}">
                <div class="info-link-icon">🔔</div>
                <div class="card-title">System Alerts</div>
                <p style="font-weight:800;font-size:15px;">{health_icon} {health_title}</p>
                <p class="resource-description">{health_message}</p>
            </div>
        </a>
        """
    )



# ============================================================
# MAIN DASHBOARD CREDIT
# ============================================================

st.markdown('<div id="about-section"></div>', unsafe_allow_html=True)

html(
    f"""
    <div class="footer">
        <div class="footer-brand">
            🌿 Kissan Seva
        </div>

        <div class="footer-text">
            For Farmers. By Technology.
        </div>

        <div style="margin-top:13px;font-size:15px;">
            Built by <b>Pradeep Kalasagond</b>
            &nbsp;·&nbsp;
            <a href="{LINKEDIN_URL}" target="_blank">
                LinkedIn ↗
            </a>
        </div>

        <div class="footer-text" style="margin-top:9px;">
            Smarter Farming. Brighter Tomorrow.
        </div>
    </div>
    """
)
