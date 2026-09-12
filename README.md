# 🌾 Kissan Seva

## AI-Powered Agricultural Market Intelligence & Farmer Decision Support Platform

Kissan Seva is an end-to-end agricultural decision-support platform that brings government mandi prices, weather intelligence, irrigation recommendations, market analytics, and machine-learning-based price direction forecasting into one application.

The goal is simple:

> **Make scattered agricultural information easier to understand and act upon.**

---

## 🚀 Live Application

🔗 [Kissan Seva — Live App](https://pradeep-kissan-seva.streamlit.app/#market-section)

💻 [GitHub Repository](https://github.com/pradeepkalasagond70-blip/kissan-seva)

---

# 📌 Problem Statement

Farmers often need to make decisions based on several different types of information:

- What is the current mandi price?
- Which market is offering a better price?
- What will the weather look like tomorrow?
- Should irrigation be done today?
- Is the market price likely to move up, down, or remain stable?

The required information exists across different sources, but collecting and interpreting it can be difficult.

**Kissan Seva brings these signals together into a single decision-support platform.**

---

# 🎯 Project Objectives

Kissan Seva was designed to:

- Provide access to current government mandi price data
- Provide weather forecasts for selected locations
- Convert rainfall information into a simple irrigation recommendation
- Analyze agricultural market prices
- Use historical mandi data for machine-learning-based price direction forecasting
- Present agricultural information through an intuitive dashboard
- Demonstrate an end-to-end Data Science workflow
- Convert raw agricultural data into actionable decision support
- Deploy the complete solution as a working application

---

# 🌾 Key Features

## 📊 1. Current Mandi Prices

Kissan Seva integrates government agricultural market data through the **AGMARKNET / data.gov.in ecosystem**.

Users can select:

**State → District → Commodity → Market**

and view available mandi records including:

- Minimum price
- Maximum price
- Modal price
- Commodity
- Market
- District
- Arrival date
- Variety
- Grade

The dashboard uses the available government API data to restrict selections to supported locations and market combinations.

---

# 🌦️ 2. Weather Intelligence

Weather information is integrated using the **Open-Meteo API**.

The platform provides:

- Current temperature
- Relative humidity
- Rainfall
- Wind speed
- Maximum temperature
- Minimum temperature
- Rain probability
- Expected precipitation
- 7-day forecast

This provides environmental context for agricultural decision-making.

---

# 💧 3. Irrigation Decision Support

Kissan Seva converts weather information into a simple irrigation recommendation.

The decision engine considers:

- Tomorrow's rainfall probability
- Expected rainfall
- Reference evapotranspiration (ET₀)
- Expected temperature

The system provides recommendations such as:

- **IRRIGATION REQUIRED**
- **IRRIGATION NOT REQUIRED**
- **IRRIGATION MAY BE REQUIRED**

The recommendation is intended as decision support and should be combined with local soil conditions, crop stage, water availability, and farmer knowledge.

---

# 📈 4. Market Analytics

The platform provides market-level price analysis including:

- Average price
- Highest observed price
- Lowest observed price
- Observed records
- Price movement
- Price trend visualization
- Market-level price comparison

This transforms raw mandi data into easier-to-understand market insights.

---

# 🤖 5. Machine Learning Price Direction Forecasting

Kissan Seva includes a machine-learning component trained using historical mandi-price data.

### Model

**Random Forest Classifier**

The model predicts the next observed market-day price direction as:

- **UP**
- **STABLE**
- **DOWN**

---

# 🔬 Feature Engineering

The model uses engineered time-series features including:

- Lag 1 price
- Lag 2 price
- Lag 3 price
- 1-day return
- 2-day return
- 3-day return
- 3-day moving average
- 7-day moving average
- 7-day volatility
- Minimum price
- Maximum price
- Modal price
- Day of week
- Month
- Number of observations

These features were created to capture short-term price movement, momentum, trend and volatility.

---

# 📊 Model Performance

The model was evaluated using a **chronological 80/20 train-test split**.

| Metric | Result |
|---|---:|
| Accuracy | **50.05%** |
| Macro F1-Score | **47.94%** |
| Balanced Accuracy | **49.74%** |

### Interpretation

The results demonstrate an important characteristic of agricultural price forecasting:

> **Short-term agricultural price direction is difficult to predict from historical market data alone.**

Rather than hiding the model's limitations, Kissan Seva reports the evaluation results transparently.

The model should therefore be considered an **experimental decision-support component**, not a guaranteed future-price prediction system.

---

# 🔬 Model Comparison

Multiple machine-learning approaches were evaluated before selecting the final model.

| Model | Accuracy | Balanced Accuracy | Macro F1 |
|---|---:|---:|---:|
| Naive STABLE Baseline | 49.91% | 33.33% | 22.20% |
| Logistic Regression | 50.39% | 47.81% | 46.89% |
| Random Forest | **50.05%** | **49.74%** | **47.94%** |
| XGBoost | 54.89% | 47.13% | 46.73% |

The **Random Forest model was selected based on Macro F1-Score**, rather than simply selecting the model with the highest raw accuracy.

This was important because the target contains three classes:

**UP / STABLE / DOWN**

---

# 🧠 Data Science Workflow

The project follows an end-to-end Data Science workflow:

```text
Problem Definition
        ↓
Data Collection
        ↓
Data Cleaning
        ↓
Exploratory Data Analysis
        ↓
Feature Engineering
        ↓
Target Creation
        ↓
Chronological Train/Test Split
        ↓
Model Training
        ↓
Model Comparison
        ↓
Model Evaluation
        ↓
Model Serialization
        ↓
FastAPI Integration
        ↓
Streamlit Application
        ↓
Testing
        ↓
Deployment
kissan-seva/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── model_service.py
│   ├── mandi_service.py
│   └── irrigation_service.py
│
├── frontend/
│   └── app.py
│
├── models/
│   └── kissan_seva_price_direction_model.joblib
│
├── data/
│
├── src/
│   ├── __init__.py
│   └── weather.py
│
├── .gitignore
├── README.md
└── requirements.txt

Testing
The application was tested across its main components:
FastAPI startup
API health endpoint
ML model loading
Mandi API connectivity
ML prediction endpoint
Irrigation decision engine
Streamlit application startup
Mandi dashboard
Price tables
Price charts
Weather interface
Dashboard interactions

🔮 Future Improvements
Potential future improvements include:
Persistent historical mandi-price database
More commodities
More markets and locations
Stronger time-series forecasting models
Improved live feature generation
Crop-specific irrigation recommendations
Soil-moisture integration
Satellite and remote-sensing data
Personalized farmer profiles
Market-distance calculations
Nearby market recommendations
Government scheme discovery
Multilingual support
Voice-based farmer assistance
Mobile-first experience
Advanced market forecasting
Better farmer-specific recommendations
Problem
   ↓
Data
   ↓
Cleaning
   ↓
EDA
   ↓
Feature Engineering
   ↓
Machine Learning
   ↓
Evaluation
   ↓
API Integration
   ↓
Application
   ↓
Testing
   ↓
Deployment

One of the biggest lessons from the project was that:
Honest model evaluation is more valuable than artificially high performance.
A model with limitations can still provide valuable learning when those limitations are understood, measured and communicated clearly.
The project also reinforced the importance of connecting technical work to a real-world problem rather than building a model simply for the sake of using machine learning.


