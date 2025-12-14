# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib

from .database import Base, engine
from .routers import predictions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# expected models are placed in repo root /models/
OFFENSE_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "playcall_model.pkl")
DEF_COVERAGE_PATH = os.path.join(BASE_DIR, "..", "models", "def_coverage_model.pkl")
DEF_FRONT_PATH = os.path.join(BASE_DIR, "..", "models", "def_front_model.pkl")
DEF_PRESSURE_PATH = os.path.join(BASE_DIR, "..", "models", "def_pressure_model.pkl")


def load_models():
    models = {}
    for name, path in [
        ("offense_model", OFFENSE_MODEL_PATH),
        ("def_coverage_model", DEF_COVERAGE_PATH),
        ("def_front_model", DEF_FRONT_PATH),
        ("def_pressure_model", DEF_PRESSURE_PATH),
    ]:
        try:
            models[name] = joblib.load(path)
            print(f"Loaded model: {path}")
        except Exception as e:
            models[name] = None
            print(f"Warning: failed loading {path}: {e}")
    return models


app = FastAPI(title="AI Playcaller API (ML-only)")

# ✅ CORS (frontend only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://id-preview--c1623c94-96be-4791-8153-5174d42cfe46.lovable.app",
        "https://lovable.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create DB tables (if still needed)
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    app.state.models = load_models()


# ✅ ML-only routes
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Playcaller API (ML-only) running"
    }


