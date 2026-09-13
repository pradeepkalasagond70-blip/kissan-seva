from fastapi import FastAPI
from pydantic import BaseModel

from backend.model_service import price_prediction_service
from backend.mandi_service import get_mandi_prices
from backend.irrigation_service import get_irrigation_recommendation

app = FastAPI(
    title="Kissan Seva API",
    description="AI-powered agricultural market decision support system",
    version="1.0.0"
)


class PredictionRequest(BaseModel):
    lag_1: float
    lag_2: float
    lag_3: float
    return_1d: float
    return_2d: float
    return_3d: float
    ma_3: float
    ma_7: float
    volatility_7d: float
    min_price: float
    max_price: float
    modal_price: float
    day_of_week: int
    month: int
    observations: int


@app.get("/")
def home():
    return {"message": "Kissan Seva API is running 🌾"}


@app.get("/model-status")
def model_status():
    return {
        "status": "loaded",
        "model": price_prediction_service.model_data["model_name"],
        "features": len(price_prediction_service.features)
    }


@app.post("/predict")
def predict_price_direction(request: PredictionRequest):
    result = price_prediction_service.predict(request.model_dump())
    return {
        "status": "success",
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    }


@app.get("/market-price")
def market_price(
    state: str | None = None,
    district: str | None = None,
    market: str | None = None,
    commodity: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    return get_mandi_prices(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        limit=limit,
        offset=offset,
    )


class WeatherRequest(BaseModel):
    weather: dict


@app.post("/irrigation")
def irrigation_recommendation(request: WeatherRequest):
    return get_irrigation_recommendation(request.weather)
