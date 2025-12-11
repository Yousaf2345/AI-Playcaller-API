# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib

from .database import Base, engine
from .routers import predictions, auth  # remove teams import if you don't have it

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

app = FastAPI(title="AI Playcaller API (v2)")

# CORS - allow Lovable preview + localhost + any dev origins (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Changed to False
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import Response

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, x-client-info, apikey",
        }
    )


# create DB tables (sqlite file created automatically)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    # attach models to app.state so routers can access them
    app.state.models = load_models()

# include routers
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(teams.router, prefix="/teams", tags=["teams"])  # optional

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Playcaller API (v2) - running"}

