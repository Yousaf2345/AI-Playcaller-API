# app/routers/predictions.py
from fastapi import APIRouter, HTTPException, Depends, Request
import pandas as pd
from app.schemas import PlayInput, DefenseRequest
from typing import Any

router = APIRouter()

# Offense endpoint
@router.post("/offense")
def predict_offense(data: PlayInput, request: Request, user=Depends(allow_guest_or_user)):
    offense_model = request.app.state.models.get("offense_model")
    if offense_model is None:
        raise HTTPException(status_code=503, detail="Offense model not available")

    df = pd.DataFrame([data.dict()])

    # engineering (same as training)
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
    probs = offense_model.predict_proba(df)[0].tolist()
    return {"predicted_play": pred, "probabilities": probs}

# Defensive combined endpoint (returns all three predictions)
@router.post("/defense")
def predict_defense(payload: DefenseRequest, request: Request,user=Depends(allow_guest_or_user)):
    models = request.app.state.models
    m_pressure = models.get("def_pressure_model")
    m_coverage = models.get("def_coverage_model")
    m_front = models.get("def_front_model")

    if any(m is None for m in [m_pressure, m_coverage, m_front]):
        raise HTTPException(status_code=503, detail="One or more defensive models not available")

    X = pd.DataFrame([{
        "down": payload.down,
        "ydstogo": payload.ydstogo,
        "yardline_100": payload.yardline_100,
        "qtr": payload.qtr,
        "score_differential": payload.score_differential,
        "quarter_seconds_remaining": payload.quarter_seconds_remaining
    }])

    pressure_pred = int(m_pressure.predict(X)[0])
    coverage_pred = m_coverage.predict(X)[0]
    front_pred = m_front.predict(X)[0]

    pressure_probs = m_pressure.predict_proba(X)[0].tolist()
    coverage_probs = m_coverage.predict_proba(X)[0].tolist()
    front_probs = m_front.predict_proba(X)[0].tolist()

    return {
        "recommended_pressure": pressure_pred,
        "recommended_coverage": coverage_pred,
        "recommended_front": front_pred,
        "probabilities": {
            "pressure": pressure_probs,
            "coverage": coverage_probs,
            "front": front_probs
        }
    }

# Optional: individual defense endpoints
@router.post("/defense/pressure")
def predict_pressure(payload: DefenseRequest, request: Request, user=Depends(allow_guest_or_user)):
    m = request.app.state.models.get("def_pressure_model")
    if m is None:
        raise HTTPException(status_code=503, detail="Pressure model not available")
    X = pd.DataFrame([payload.dict()])
    p = int(m.predict(X)[0])
    probs = m.predict_proba(X)[0].tolist()
    return {"recommended_pressure": p, "probabilities": probs}

@router.post("/defense/coverage")
def predict_coverage(payload: DefenseRequest, request: Request, user=Depends(allow_guest_or_user)):
    m = request.app.state.models.get("def_coverage_model")
    if m is None:
        raise HTTPException(status_code=503, detail="Coverage model not available")
    X = pd.DataFrame([payload.dict()])
    p = m.predict(X)[0]
    probs = m.predict_proba(X)[0].tolist()
    return {"recommended_coverage": p, "probabilities": probs}

@router.post("/defense/front")
def predict_front(payload: DefenseRequest, request: Request, user=Depends(allow_guest_or_user)):
    m = request.app.state.models.get("def_front_model")
    if m is None:
        raise HTTPException(status_code=503, detail="Front model not available")
    X = pd.DataFrame([payload.dict()])
    p = m.predict(X)[0]
    probs = m.predict_proba(X)[0].tolist()
    return {"recommended_front": p, "probabilities": probs}

