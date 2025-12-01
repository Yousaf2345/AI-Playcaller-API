# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib

from .routers import predictions, auth  # teams router optional; if you don't have it remove this import
from .database import Base, engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute model paths (project root /models/)
OFFENSE_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "playcall_model.pkl")
DEF_COVERAGE_PATH = os.path.join(BASE_DIR, "..", "models", "def_coverage_model.pkl")
DEF_FRONT_PATH = os.path.join(BASE_DIR, "..", "models", "def_front_model.pkl")
DEF_PRESSURE_PATH = os.path.join(BASE_DIR, "..", "models", "def_pressure_model.pkl")

app = FastAPI(title="AI Playcaller API (v2)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create DB tables (sqlite by default) - safe to call on startup
Base.metadata.create_all(bind=engine)


def load_models():
    models = {}
    paths = {
        "offense_model": OFFENSE_MODEL_PATH,
        "def_coverage_model": DEF_COVERAGE_PATH,
        "def_front_model": DEF_FRONT_PATH,
        "def_pressure_model": DEF_PRESSURE_PATH,
    }
    for name, path in paths.items():
        try:
            models[name] = joblib.load(path)
            print(f"[startup] Loaded model: {path}")
        except Exception as e:
            models[name] = None
            print(f"[startup] Warning: failed loading {path}: {e}")
    return models


@app.on_event("startup")
def on_startup():
    # attach models dict to app.state so routers can access them via request.app.state.models
    app.state.models = load_models()


# include routers
app.include_router(predictions.router, prefix="", tags=["predictions"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
# include teams router if you have it, otherwise remove/comment next line




@app.get("/")
def root():
    return {"status": "ok", "message": "AI Playcaller API (v2) - running"}
