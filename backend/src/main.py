from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import scan, scan_issues, services
from src.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Infrastructure Registry", lifespan=lifespan)
app.include_router(scan.router)
app.include_router(services.router)
app.include_router(scan_issues.router)
