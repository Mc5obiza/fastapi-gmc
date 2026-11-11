from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from datetime import datetime, timezone
from pathlib import Path
from backend.app.routers import quizz
from backend.app.routers import summarize
from backend.app.routers import chat, flashcard
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(chat.router)
app.include_router(quizz.router)
app.include_router(summarize.router)
app.include_router(flashcard.router)
# Created an endpoint that runs root function
@app.get("/")
def root():
    return {
        "status":"ok",
        "message":"Welcome To the AI Assistant backend"
    }

@app.get("/about")
def about():
    return {
        "status":"ok",
        "Title":"AI Student assistant",
        "Description":"it helps students"
    }

@app.get("/health")
def health():
    return {
        "status":"ok",
        "message":"API IS RUNNING",
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "version":"0.2.0"
    }

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")
