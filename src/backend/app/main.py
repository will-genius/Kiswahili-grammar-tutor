from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.api import session

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

app.include_router(session.router, prefix="/session", tags=["Session"])

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "offline-edge-ready"}