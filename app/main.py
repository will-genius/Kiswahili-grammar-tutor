from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
import app.models
from app.session import router as session_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on server start
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(session_router, prefix="/session", tags=["Session"])

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "offline-edge-ready"}



# run using uvicorn app.main:app --reload --port 8000