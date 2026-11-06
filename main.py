from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from datetime import datetime, timezone
from routers import chat,quizz,summarize,flashcard
app = FastAPI()
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
