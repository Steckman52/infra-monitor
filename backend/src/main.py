from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import (
    adrs,
    compatibility,
    connections,
    error_groups,
    log_scan,
    log_scan_issues,
    scan,
    scan_issues,
    services,
)
from src.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Infrastructure Registry", lifespan=lifespan)
app.include_router(scan.router)
app.include_router(services.router)
app.include_router(scan_issues.router)
app.include_router(compatibility.router)
app.include_router(connections.router)
app.include_router(log_scan.router)
app.include_router(error_groups.router)
app.include_router(log_scan_issues.router)
app.include_router(adrs.router)
