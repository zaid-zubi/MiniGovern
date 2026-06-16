from fastapi import Depends, FastAPI
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.db.session import get_db
from app.views.auth import router as auth_router
from app.views.datasources import router as datasources_router
from app.views.scan_job import router as scan_job_router
from app.views.tags import router as tags_router
from app.views.categories import router as category_router
from app.views.datasets import router as dataset_router
from app.views.catalog import router as catalog_router
from core.settings.base_exception import AppException
from core.settings.constants import ResponseMessages, Error
from core.settings.exceptions.datasource import DatasourceConnectionFailed
from core.settings.response import http_response

app = FastAPI(title="MiniGovern", debug=settings.debug)
app.include_router(auth_router)
app.include_router(datasources_router)
app.include_router(scan_job_router)
app.include_router(tags_router)
app.include_router(category_router)
app.include_router(dataset_router)
app.include_router(catalog_router)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "env": settings.app_env,
        "database": "connected",
    }


from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(DatasourceConnectionFailed)
async def datasource_connection_failed_handler(
        request: Request,
        exc: DatasourceConnectionFailed,
):
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "success": False,
            "message": Error.DATABASE_CONNECTION_FAILUER,
            "error": None
        },
    )
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
        },
    )