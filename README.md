# 🌾 Kissan Seva

## AI-Powered Agricultural Market & Weather Decision Support Platform

Kissan Seva is an end-to-end agricultural decision-support platform that combines government mandi market data, weather intelligence, machine learning, data analytics, and rule-based irrigation recommendations into a single application.

The goal of the project is to transform fragmented agricultural data into simple, actionable insights for farmers.

---

## 🚀 Live Application

**Live Demo:**  
https://pradeep-kissan-seva.streamlit.app/

**GitHub Repository:**  
https://github.com/pradeepkalasagond70-blip/kissan-seva

---

# 🎯 Problem Statement

Farmers often need multiple pieces of information before making agricultural decisions:

- What is the current mandi price?
- Which market is currently reporting a better price?
- Is rain expected?
- Should irrigation be performed?
- Is the market price moving upward, downward, or remaining stable?
- What are the upcoming weather conditions?

This information is often distributed across different sources.

Kissan Seva brings these data points together into one decision-support platform.

---

# 💡 Project Objective

The objective of Kissan Seva is to demonstrate how Data Science, Machine Learning, APIs, and application development can be combined to solve a practical agricultural problem.

The project follows an end-to-end pipeline:

   text
Agricultural Data
       ↓
Data Engineering
       ↓
Exploratory Data Analysis
       ↓
Feature Engineering
       ↓
Machine Learning
       ↓
Decision Engines
       ↓
REST APIs
       ↓
Interactive Dashboard
       ↓
Actionable Insights
✨ Key Features

1. 🏪 Current Mandi Prices
Kissan Seva retrieves current daily mandi market information using the Government of India's data.gov.in API.
Users can explore market information through dependent selections:

State
  ↓
District
  ↓
Commodity
  ↓
Market

The dashboard displays:
- State
- District
- Market
- Commodity
- Variety
- Grade
- Arrival Date
- Minimum Price
- Maximum Price
- Modal Price

Important:
The availability of states, districts, commodities, and markets depends on the records returned by the current government data source.
The application does not artificially create market records that are not present in the source data.

2. 🌦️ Weather Intelligence
Kissan Seva integrates the Open-Meteo Weather API to provide weather information.
The application provides:
- Current temperature
- Relative humidity
- Rainfall
- Rain probability
- Wind speed
- Expected rainfall
- Maximum temperature
- Minimum temperature
- ET₀ / reference evapotranspiration
- 7-day weather forecast

3. 📍 Location Intelligence
The Open-Meteo Geocoding API converts a location name into geographical coordinates.
The system retrieves:
- Location
- Latitude
- Longitude
- Country

These coordinates are then used to retrieve weather information.

4. 💧 Irrigation Decision Engine
Kissan Seva includes a rule-based irrigation decision engine.
The engine evaluates weather forecast variables including:
- Rain probability
- Expected rainfall
- ET₀
- Maximum temperature

The system generates recommendations such as:
- IRRIGATION REQUIRED
- IRRIGATION MAY BE REQUIRED
- IRRIGATION NOT REQUIRED

Each recommendation includes an explanation of the conditions behind the decision.

Example Decision Logic:
High rainfall probability
+
Sufficient expected rainfall
        ↓
IRRIGATION NOT REQUIRED

Low rainfall
+
Higher estimated water loss
        ↓
IRRIGATION REQUIRED

The irrigation engine is designed as a decision-support component and does not replace field-level soil measurements or professional agricultural advice.

5. 🤖 Machine Learning — Market Price Direction
Kissan Seva includes a machine learning model that predicts the direction of the next observed market-day price movement.
The model predicts three classes:
- UP
- STABLE
- DOWN

The model does not attempt to guarantee or predict an exact future market price.
Instead, the problem is treated as a three-class classification task.

6. 📊 Market Analytics
The dashboard provides market-level analytical information using the available mandi records.
Analytics include:
- Current market price comparison
- Minimum price
- Maximum price
- Modal price
- Market-level records
- Price comparison charts
- Market observations
- Price analysis

7. 📈 Price Trend Visualization
Kissan Seva uses interactive dashboard visualizations to help users understand market information.
Visualizations include:
- Market price comparison
- Price-related charts
- Temperature trends
- Rainfall trends
- Weather forecast information

8. 🌧️ 7-Day Weather Forecast
The application provides a 7-day weather view containing:
- Date
- Maximum temperature
- Minimum temperature
- Rain probability
- Expected rainfall
- ET₀
This information also supports the irrigation decision engine.

9. 🧠 AI Market Outlook
The machine learning component provides an estimated market direction:
- UP
- STABLE
- DOWN

The application also displays the model's prediction confidence when available.
This should be interpreted as an experimental ML-based signal rather than a guaranteed market prediction.

🧠 Machine Learning Pipeline
The machine learning workflow follows:

Historical Mandi Dataset
        ↓
Data Cleaning
        ↓
Exploratory Data Analysis
        ↓
Market-Level Aggregation
        ↓
Feature Engineering
        ↓
Target Engineering
        ↓
Chronological Train/Test Split
        ↓
Model Training
        ↓
Model Comparison
        ↓
Model Selection
        ↓
Model Serialization
        ↓
FastAPI Prediction API
        ↓
Streamlit Dashboard

📊 Historical Dataset
The primary machine learning experiment focused on Green Chilli market prices.
After data preparation:
- Green Chilli Records        : 104,266
- Unique Dates                : 365
- States                      : 8
- Market Combinations         : ~514
- Valid Records               : 104,254
- ML-Ready Observations       : 100,318

The data was aggregated at the market/date level.
The prepared dataset contained:
- State
- District
- Market
- Commodity
- Price Date
- Minimum Price
- Maximum Price
- Modal Price
- Number of observations

⚠️ Historical Dataset Limitation
The historical ML dataset used for this experiment does not contain Karnataka.
Therefore, Karnataka was not artificially added to the historical training data.
Current government mandi data and historical ML training data are treated as separate data sources.
This means a market can appear in the current mandi system even if that market was not present in the historical ML training dataset.

🧹 Data Cleaning
The data preparation pipeline included:
- Date parsing
- Numeric conversion
- Missing-value analysis
- Duplicate detection
- Market-level aggregation
- State/district/market grouping
- Price validation
- Invalid record removal

A logical price relationship was checked:
Minimum Price ≤ Modal Price ≤ Maximum Price

Invalid price relationships were removed before machine learning preparation.

🔬 Exploratory Data Analysis
EDA was performed to understand:
- Price distributions
- State coverage
- Market coverage
- Commodity observations
- Market continuity
- Daily price movement
- Price volatility
- Observation frequency
- Data quality

The analysis showed differences in market observation frequency and continuity across markets.

⚙️ Feature Engineering
The following features were created for the machine learning model.

Lag Features:
- lag_1
- lag_2
- lag_3
These represent previous observed market prices.

Return Features:
- return_1d
- return_2d
- return_3d
These represent recent percentage price movements.

Moving Average Features:
- ma_3
- ma_7
These capture short-term price trends.

Volatility Feature:
- volatility_7d
This captures recent price variability.

Price Features:
- min_price
- max_price
- modal_price

Temporal Features:
- day_of_week
- month

Observation Feature:
- observations

🎯 Target Engineering
The target represents the movement of the next observed market-day price.
A ±2% threshold was used:

Change > +2%
    ↓
UP

Change between -2% and +2%
    ↓
STABLE

Change < -2%
    ↓
DOWN

This created a three-class classification problem.

🧪 Machine Learning Models Evaluated
Multiple models were evaluated:
- Naive STABLE Baseline
- Logistic Regression
- Random Forest Classifier
- XGBoost Classifier

The purpose was to compare different approaches instead of assuming that one algorithm would automatically perform best.

📈 Model Evaluation
The models were evaluated using:
- Accuracy
- Balanced Accuracy
- Macro F1 Score

Results:
| Model | Accuracy | Balanced Accuracy | Macro F1 |
|---|---|---|---|
| Naive STABLE Baseline | 49.91% | 33.33% | 22.20% |
| Logistic Regression | 50.39% | 47.81% | 46.89% |
| Random Forest | 50.05% | 49.74% | 47.94% |
| XGBoost | 54.89% | 47.13% | 46.73% |

🏆 Selected Model
Random Forest Classifier
Random Forest was selected primarily based on Macro F1 and Balanced Accuracy, rather than selecting the model only because of raw accuracy.
This provided a more balanced evaluation across UP, STABLE, and DOWN.

🔎 Feature Importance
Important features identified by the Random Forest model included:
- volatility_7d
- return_1d
- return_2d
- return_3d
- month
- ma_7
- modal_price
- min_price
- max_price
- ma_3

Recent price movement and volatility were among the most important model features.

🏗️ System Architecture
                         ┌─────────────────────────┐
                         │ Government of India     │
                         │       data.gov.in       │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Mandi Service       │
                         │   Current Market Data   │
                         └────────────┬────────────┘
                                      │
                                      ▼
┌──────────────────────┐     ┌──────────────────────┐
│ Historical Mandi     │────▶│ Data Processing & ML │
│ Dataset              │     │ Feature Engineering  │
└──────────────────────┘     └──────────┬───────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Random Forest   │
                               │ UP/STABLE/DOWN  │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ FastAPI Backend │
                               └────────┬────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │                     │                     │
                  ▼                     ▼                     ▼
            Market API            Prediction API       Irrigation API
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Streamlit UI    │
                               └────────┬────────┘
                                        ▲
                                        │
                               ┌─────────────────┐
                               │  Open-Meteo API │
                               │ Weather + Geo   │
                               └─────────────────┘

🔌 External APIs & Data Sources

🇮🇳 Government of India — data.gov.in
Kissan Seva uses the Government of India's open-data platform for current mandi information.

Dataset:
Current Daily Price of Various Commodities from Various Markets (Mandi)

Resource ID:
9ef84268-d588-465a-a308-a864a43d0070

Main Fields:
- State
- District
- Market
- Commodity
- Variety
- Grade
- Arrival Date
- Min Price
- Max Price
- Modal Price

The source provides daily/current market records. It is not a continuously streaming tick-level market feed.

🌦️ Open-Meteo Weather API
Used for:
- Current weather
- Temperature
- Humidity
- Rainfall
- Rain probability
- Wind speed
- Precipitation
- ET₀
- 7-day forecast

📍 Open-Meteo Geocoding API
Used for:
- Location name
- Latitude
- Longitude
- Country

The coordinates are then used to retrieve weather information.

🛠️ Technology Stack
- Programming Language: Python
- Data Science: Pandas, NumPy
- Machine Learning: Scikit-learn, XGBoost, Joblib
- Backend: FastAPI, Pydantic, Uvicorn
- Frontend: Streamlit, Custom CSS
- Data Visualization: Matplotlib, Streamlit Charts
- API Integration: Requests, Government of India data.gov.in API, Open-Meteo Weather API, Open-Meteo Geocoding API
- Environment Management: python-dotenv, .env
- Development Tools: Visual Studio Code, Google Colab, Jupyter Notebooks, Git, GitHub
- Deployment: Streamlit Community Cloud

📁 Project Structure
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
├── .env
├── .gitignore
├── README.md
└── requirements.txt

🔗 FastAPI Backend Endpoints

Health Check:
GET /
Checks whether the Kissan Seva API is running.

Model Status:
GET /model-status
Returns model status, model name, and number of model features.

Current Mandi Prices:
GET /market-price
Supported parameters: state, district, market, commodity, limit
Example: /market-price?state=Karnataka&commodity=Green%20Chilli

ML Price Direction Prediction:
POST /predict
Accepts engineered ML features and returns a price-direction prediction.
Example response:
{
    "status": "success",
    "prediction": "UP",
    "confidence": 72.45
}
Possible predictions: UP, STABLE, DOWN

Irrigation Recommendation:
POST /irrigation
Accepts weather forecast data and returns irrigation recommendation, explanation, rain probability, expected rainfall, ET₀, and maximum temperature.

🔐 Environment Variables
The Government API key is stored using an environment variable.
Create a .env file:
DATA_GOV_API_KEY=YOUR_API_KEY

The .env file should never be committed to GitHub.
The .gitignore file contains: .env

▶️ Run Locally

1. Clone the Repository:
git clone https://github.com/pradeepkalasagond70-blip/kissan-seva.git
cd kissan-seva

2. Create a Virtual Environment:
python -m venv .venv

Windows:
.venv\Scripts\activate

3. Install Dependencies:
pip install -r requirements.txt

4. Configure Environment Variables:
Create `.env` and add:
DATA_GOV_API_KEY=YOUR_API_KEY

5. Start FastAPI:
uvicorn backend.main:app --reload

API: http://127.0.0.1:8000
Swagger documentation: http://127.0.0.1:8000/docs

6. Start Streamlit:
Open another terminal:
streamlit run frontend/app.py

Dashboard: http://localhost:8501

🧪 Testing
The application was tested across its major components.

Backend Testing:
✓ FastAPI startup
✓ Health endpoint
✓ ML model loading
✓ Government mandi API integration
✓ Price prediction endpoint
✓ Irrigation endpoint

Frontend Testing:
✓ Streamlit startup
✓ FastAPI communication
✓ Mandi data rendering
✓ Weather rendering
✓ ML prediction display
✓ Irrigation recommendation
✓ Charts
✓ Dashboard navigation

🔄 End-to-End Application Flow
User
 │
 ▼
Select State
 │
 ▼
Select District
 │
 ▼
Select Commodity
 │
 ▼
Select Market
 │
 ├──────────────────────┐
 │                      │
 ▼                      ▼
Mandi API            Weather API
 │                      │
 ▼                      ▼
Current Price        Forecast
 │                      │
 │                      ▼
 │              Irrigation Engine
 │                      │
 └──────────┬───────────┘
            │
            ▼
      Market Analysis
            │
            ▼
     ML Price Direction
            │
            ▼
      UP / STABLE / DOWN
            │
            ▼
    Streamlit Dashboard

⚠️ Limitations
Kissan Seva is an MVP and has several limitations.

1. Current Mandi Data
The Government mandi source provides daily/current market records rather than a continuously streaming real-time market feed. Therefore, the application uses the term current mandi data rather than tick-level live pricing.

2. Market Availability
The available state, district, commodity, and market combinations depend on the records returned by the current government data source. A particular market or district may not appear if there is no corresponding current record returned by the source.

3. ML Performance
The current model achieved:
- Accuracy: 50.05%
- Balanced Accuracy: 49.74%
- Macro F1: 47.94%
This is not production-grade predictive accuracy. The ML component should therefore be considered an experimental decision-support component, not a guaranteed market prediction system.

4. Historical Dataset Coverage
The historical dataset used for ML training does not contain Karnataka. Therefore, the ML model should not be interpreted as having complete nationwide historical representation.

5. Live ML Feature Generation
The model was trained using historical engineered features such as lagged prices, returns, moving averages, volatility, temporal features, and market observations. Generating all of these historical features reliably from current API observations is a separate data-engineering challenge and remains an area for future improvement.

🔮 Future Improvements
Potential future versions of Kissan Seva could include:
- Larger historical datasets
- More commodities
- More states
- More markets
- Automated historical data ingestion
- Robust historical feature generation
- Commodity-specific ML models
- Market-specific ML models
- Time-series forecasting
- Advanced feature engineering
- Hyperparameter optimization
- Model monitoring
- Confidence calibration
- Soil-moisture integration
- Crop-specific irrigation models
- Satellite/agricultural data integration
- Farmer-specific recommendations
- Multilingual support
- Voice-based farmer assistant
- SMS/WhatsApp alerts
- Mobile application
- Automated market alerts

📚 Key Learning Outcomes
This project was developed as an end-to-end Data Science and application engineering project rather than only a machine learning notebook.

Data Engineering:
- Large dataset handling
- Data cleaning
- Data validation
- Aggregation
- Market-level data preparation
- External API integration

Data Analysis:
- Exploratory Data Analysis
- Distribution analysis
- Market coverage analysis
- Price movement analysis
- Volatility analysis

Machine Learning:
- Feature engineering
- Target engineering
- Classification
- Chronological train/test splitting
- Model comparison
- Class imbalance evaluation
- Macro F1
- Balanced Accuracy
- Model serialization

Backend Engineering:
- FastAPI
- REST API development
- Pydantic
- Service-based architecture
- External API integration
- Error handling

Frontend Engineering:
- Streamlit
- Custom CSS
- Dashboard design
- API consumption
- Interactive charts
- User-driven filtering

Deployment:
- Git
- GitHub
- Environment variables
- Streamlit Cloud deployment

🧠 Engineering Approach
Kissan Seva was built around a simple engineering principle:

Raw Data
   ↓
Understand the Data
   ↓
Engineer Useful Features
   ↓
Build Intelligence
   ↓
Expose Intelligence Through APIs
   ↓
Build a Usable Interface
   ↓
Deploy the Product

The project demonstrates the complete journey from raw agricultural data to a deployed decision-support application.

🌾 Why Kissan Seva?
Agriculture generates large amounts of data across markets, prices, weather, rainfall, supply, demand, and crop conditions. However, raw data alone does not create value. The challenge is converting fragmented information into understandable information that can support decisions.

Kissan Seva demonstrates how:

DATA
  ↓
INTELLIGENCE
  ↓
DECISION

can be applied to an agricultural use case.

👨‍💻 Author
Pradeep Kalasagond
Data Science & Analytics | Python | Machine Learning | Data Analytics | AI Applications
LinkedIn: https://www.linkedin.com/in/pradeep-kalasagond-95579a230
GitHub: https://github.com/pradeepkalasagond70-blip

⭐ Project
If you find Kissan Seva useful or interesting, consider giving the repository a ⭐.

🌾 Kissan Seva
Turning Agricultural Data Into Actionable Intelligence.
Built with Python • Data Science • Machine Learning • FastAPI • Streamlit • Government APIs • Weather APIs
