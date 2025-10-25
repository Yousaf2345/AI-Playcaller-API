from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

# Load model
model = joblib.load("playcall_model.pkl")

# Define the input schema
class PlayInput(BaseModel):
    down: int
    ydstogo: int
    yrdline100: int
    qtr: int
    ScoreDiff: float


# Initialize FastAPI
app = FastAPI()

# ✅ Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
def predict_play(data: PlayInput):
    try:
        df = pd.DataFrame([data.dict()])

        # Feature engineering
        df["red_zone"] = df["yrdline100"] <= 20
        df["short_yard"] = df["ydstogo"] <= 2
        df["third_long"] = (df["down"] == 3) & (df["ydstogo"] >= 8)
        df["half"] = df["qtr"].apply(lambda x: 1 if x in [1, 2] else 0)

        # Order features
        features = [
        "down",
        "ydstogo",
        "qtr",
        "yrdline100",
        "red_zone",
        "short_yard",
        "third_long",
        "half",
        "ScoreDiff"
        ]
        df = df[features]
        # Make prediction
        prediction = model.predict(df)[0]
        confidence = float(max(model.predict_proba(df)[0]))

        return {
            "predicted_play": prediction,
            "confidence": round(confidence, 3)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

