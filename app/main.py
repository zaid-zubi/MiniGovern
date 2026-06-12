from fastapi import Depends, FastAPI
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.db.session import get_db
from app.views.auth import router as auth_router
from app.views.datasources import router as datasources_router

app = FastAPI(title="MiniGovern", debug=settings.debug)
app.include_router(auth_router)
app.include_router(datasources_router)

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "env": settings.app_env,
        "database": "connected",
    }