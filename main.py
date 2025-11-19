from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import joblib
# ---------------------------
# Load Offensive Model
# ---------------------------


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load offensive model
OFFENSE_MODEL_PATH = os.path.join(BASE_DIR, "models", "playcall_model.pkl")
offense_model = joblib.load(OFFENSE_MODEL_PATH)

# Load defensive models
DEF_COVERAGE_PATH = os.path.join(BASE_DIR, "models", "def_coverage_model.pkl")
DEF_FRONT_PATH = os.path.join(BASE_DIR, "models", "def_front_model.pkl")
DEF_PRESSURE_PATH = os.path.join(BASE_DIR, "models", "def_pressure_model.pkl")

def_coverage_model = joblib.load(DEF_COVERAGE_PATH)
def_front_model = joblib.load(DEF_FRONT_PATH)
def_pressure_model = joblib.load(DEF_PRESSURE_PATH)



# ---------------------------
#  Input Schemas
# ---------------------------
class PlayInput(BaseModel):
    down: int
    ydstogo: int
    yrdline100: int
    qtr: int
    ScoreDiff: float


class DefenseRequest(BaseModel):
    down: int
    ydstogo: int
    yardline_100: int
    qtr: int
    score_differential: int
    quarter_seconds_remaining: int


# ---------------------------
# Initialize FastAPI
# ---------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# Offensive Prediction Route
# ---------------------------
@app.post("/predict")
def predict_play(data: PlayInput):
    try:
        df = pd.DataFrame([data.dict()])

        # Offensive feature engineering
        df["red_zone"] = df["yrdline100"] <= 20
        df["short_yard"] = df["ydstogo"] <= 2
        df["third_long"] = (df["down"] == 3) & (df["ydstogo"] >= 8)
        df["half"] = df["qtr"].apply(lambda x: 1 if x in [1, 2] else 0)

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

        prediction = model.predict(df)[0]
        confidence = float(max(model.predict_proba(df)[0]))

        return {
            "predicted_play": prediction,
            "confidence": round(confidence, 3)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ---------------------------
# Defensive Prediction Route
# ---------------------------
@app.post("/predict_defense")
def predict_defense(request: DefenseRequest):

    # EXACT feature order used during training
    X = pd.DataFrame([{
        "down": request.down,
        "ydstogo": request.ydstogo,
        "yardline_100": request.yardline_100,
        "qtr": request.qtr,
        "score_differential": request.score_differential,
        "quarter_seconds_remaining": request.quarter_seconds_remaining
    }])

    # Predictions
    pressure_pred = def_pressure_model.predict(X)[0]
    coverage_pred = def_coverage_model.predict(X)[0]
    front_pred = def_front_model.predict(X)[0]

    # Probabilities
    pressure_probs = def_pressure_model.predict_proba(X)[0].tolist()
    coverage_probs = def_coverage_model.predict_proba(X)[0].tolist()
    front_probs = def_front_model.predict_proba(X)[0].tolist()

    return {
        "recommended_pressure": int(pressure_pred),
        "recommended_coverage": coverage_pred,
        "recommended_front": front_pred,
        "probabilities": {
            "pressure": pressure_probs,
            "coverage": coverage_probs,
            "front": front_probs
        }
    }

