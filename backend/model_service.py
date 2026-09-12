import joblib
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Model Path
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "kissan_seva_price_direction_model.joblib"
)


# --------------------------------------------------
# Price Prediction Service
# --------------------------------------------------

class PricePredictionService:

    def __init__(self):

        # Load saved ML model
        self.model_data = joblib.load(MODEL_PATH)

        self.model = self.model_data["model"]
        self.features = self.model_data["features"]
        self.threshold = self.model_data["threshold"]
        self.target_mapping = self.model_data["target_mapping"]

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    def predict(self, input_data):

        # Convert input into DataFrame
        X = pd.DataFrame([input_data])

        # Keep exactly the features used during training
        X = X[self.features]

        # Generate prediction
        prediction = int(
            self.model.predict(X)[0]
        )

        # Convert numeric prediction to label
        label = self.target_mapping[prediction]

        # Calculate confidence
        confidence = None

        if hasattr(self.model, "predict_proba"):

            probabilities = self.model.predict_proba(X)[0]

            confidence = float(
                max(probabilities) * 100
            )

        return {
            "prediction": label,
            "confidence": (
                round(confidence, 2)
                if confidence is not None
                else None
            )
        }


# --------------------------------------------------
# Create Service Instance
# --------------------------------------------------

price_prediction_service = PricePredictionService()