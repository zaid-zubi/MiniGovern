from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from app.db.session import get_db

app = FastAPI(title="MiniGovern", debug=settings.debug)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "env": settings.app_env,
        "database": "connected",
    }