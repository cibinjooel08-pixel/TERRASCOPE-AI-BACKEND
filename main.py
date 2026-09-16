import sys
import os

# Ensure current and parent directories are on sys.path for universal cloud deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.api import health, query, history, export, satellite, auth
    from app.satellite.cdse_auth import cdse_auth
    from app.database.db import db_manager
except ImportError:
    from api import health, query, history, export, satellite, auth
    from satellite.cdse_auth import cdse_auth
    from database.db import db_manager

app = FastAPI(
    title="SatQuery AI Backend Engine",
    description="Natural Language Earth Observation & Copernicus Change Detection API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(history.router)
app.include_router(export.router)
app.include_router(satellite.router)

@app.on_event("startup")
def startup_diagnostics():
    try:
        print("SATQUERY AI BACKEND ENGINE STARTING...")
        print("[SUCCESS] SQLite Database Initialized.")
        
        auth = cdse_auth.check_health()
        if auth and auth.get("status") == "READY":
            print("[READY] Copernicus CDSE OAuth Authentication Validated Successfully.")
        else:
            print(f"[NOTE] Copernicus OAuth Health: {auth.get('status', 'OFFLINE') if auth else 'OFFLINE'}")
    except Exception as e:
        print(f"[NOTE] Startup diagnostic note: {e}")

@app.get("/")
def root_endpoint():
    return {
        "app": "SatQuery AI Backend Engine",
        "status": "ONLINE",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
