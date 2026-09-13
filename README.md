# 🌾 Kissan Seva
> **Turning Agricultural Data Into Actionable Intelligence**

Kissan Seva is an end-to-end decision-support platform that unifies real-time government mandi market data, weather intelligence, machine learning price direction models, and automated irrigation recommendations into a single Streamlit interface.

[🚀 Live Application ](https://pradeep-kissan-seva.streamlit.app/) | [📁 GitHub Repository](https://github.com/pradeepkalasagond70-blip/kissan-seva)

---

## 🎯 The Problem & Solution

Farmers face fragmented decision-making—mandi prices, rain forecasts, and price trends live across disconnected platforms. **Kissan Seva** aggregates these signals into a unified advisory dashboard:

- **Mandi Transparency:** Real-time daily prices (Min, Max, Modal) via Government of India APIs.
- **Irrigation Engine:** Rule-based decision-making driven by ET₀ (evapotranspiration) and 7-day weather trends.
- **Price Outlook:** Machine learning model predicting next-market-day price direction (**UP**, **STABLE**, **DOWN**).

---

## ✨ Core Features

| Feature | Source / Mechanism | Key Output |
|---|---|---|
| **Mandi Market Data** | [data.gov.in API](https://data.gov.in/) | State ➔ District ➔ Commodity ➔ Market lookup with daily arrival rates & price ranges |
| **Weather Intelligence** | [Open-Meteo API](https://open-meteo.com/) | Temperature, humidity, rain probability, wind speed, & ET₀ calculations |
| **Location Intelligence** | [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) | Automatic coordinate translation for local weather retrieval |
| **Irrigation Advisor** | Rule-Based Engine | Advises `REQUIRED`, `MAY BE REQUIRED`, or `NOT REQUIRED` based on water-loss metrics |
| **AI Price Outlook** | Random Forest Classifier | Classifies upcoming market price direction with prediction confidence |

---

## 🤖 Machine Learning Pipeline

The ML component focuses on short-term price direction classification for **Green Chilli** across 100,000+ market records (~514 markets).

### Workflow & Performance
1. **Target:** 3-class classification (**UP**: >+2%, **STABLE**: -2% to +2%, **DOWN**: <-2%).
2. **Features:** Lagged prices (`lag_1..3`), returns (`return_1d..3d`), moving averages (`ma_3`, `ma_7`), 7-day volatility, and temporal signals.
3. **Model Selection:** Selected **Random Forest Classifier** over XGBoost and Logistic Regression for superior **Macro F1** and **Balanced Accuracy** on imbalanced data.

| Model | Accuracy | Balanced Accuracy | Macro F1 |
|---|---|---|---|
| Naive STABLE Baseline | 49.91% | 33.33% | 22.20% |
| Logistic Regression | 50.39% | 47.81% | 46.89% |
| **Random Forest (Selected)** | **50.05%** | **49.74%** | **47.94%** |
| XGBoost | 54.89% | 47.13% | 46.73% |

> **Key Predictors:** `volatility_7d`, `return_1d`, `return_2d`, and `ma_7` were identified as the strongest price direction indicators.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend & Data Viz:** Streamlit, Matplotlib, Custom CSS
- **Data & ML:** Pandas, NumPy, Scikit-learn, XGBoost, Joblib
- **External APIs:** Government of India Open Data ([data.gov.in](https://data.gov.in/)), Open-Meteo Weather & Geocoding

---

⚠️ Key Considerations & Limitations
Government API Dependency: Market availability strictly mirrors active records uploaded to data.gov.in.

Experimental ML: The price direction model operates as an experimental signal (F1: 47.94%) and should be used as decision-support, not financial advice.

Dataset Scope: The historical ML training dataset excludes Karnataka records, though live mandi prices work nationwide.

Author
Pradeep Kalasagond

Data Science & Analytics | Machine Learning | AI Applications

LinkedIn Profile | GitHub Profile

⭐ If you find Kissan Seva useful, consider starring the GitHub Repository!



