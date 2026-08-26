import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.sqlite_db import init_db
from app.database.repositories import MeetingRepository
from sample_data.seed_data import seed_data
from app.api.meeting_routes import router as meeting_router
from app.api.search_routes import router as search_router
from app.api.decision_routes import router as decision_router
from app.api.memory_routes import router as memory_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB and seed if empty
    print("[Main] Initializing database...")
    init_db()
    
    repo = MeetingRepository()
    meetings = repo.list_meetings()
    if not meetings:
        print("[Main] Database is empty. Seeding core scenario sample meetings...")
        try:
            seed_data()
        except Exception as e:
            print(f"[Main] Seeding warning: {e}")
            
    yield
    print("[Main] Shutdown completed.")

app = FastAPI(
    title="AI Meeting Memory & Decision Reconstruction API",
    description="GenAI System for persistent organizational memory and decision reasoning reconstruction.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meeting_router)
app.include_router(search_router)
app.include_router(decision_router)
app.include_router(memory_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Meeting Memory & Decision Reconstruction Platform is running.",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
