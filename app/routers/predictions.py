# app/routers/predictions.py
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import pandas as pd

router = APIRouter()

class PlayInput(BaseModel):
    down: int
    ydstogo: int
    yrdline100: int
    qtr: int
    ScoreDiff: float

@router.post("/predict")
def predict_play(data: PlayInput, request: Request):
    models = request.app.state.models
    offense_model = models.get("offense_model")
    if offense_model is None:
        raise HTTPException(status_code=500, detail="Offense model not loaded on server")

    df = pd.DataFrame([data.dict()])
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
        "ScoreDiff",
    ]
    df = df[features]
    pred = offense_model.predict(df)[0]
    conf = float(max(offense_model.predict_proba(df)[0]))
    return {"predicted_play": pred, "confidence": round(conf, 3)}

