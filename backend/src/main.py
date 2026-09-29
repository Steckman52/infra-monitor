import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.api import (
    adr_issues,
    adrs,
    compatibility,
    connections,
    dashboard,
    error_groups,
    filesystem,
    log_scan,
    log_scan_issues,
    scan,
    scan_issues,
    services,
)
from src import config
from src.db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
)
logger = logging.getLogger("infra_monitor")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    logger.info("Started. Database initialised.")
    yield


app = FastAPI(title="Infrastructure Registry", lifespan=lifespan)

# The API has no authentication, by design: it is a single-user tool bound
# to localhost. That assumption only holds while the Host header is one we
# recognise -- without this, a page the user visits can re-point its own
# hostname at 127.0.0.1 (DNS rebinding), at which point the browser treats
# the backend as same-origin and can read every response, including file
# contents the scan collected.
# The port is stripped before comparison, so bare hostnames are correct here.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", *config.EXTRA_ALLOWED_HOSTS],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Without this, an unexpected failure reached the user as a bare 500
    and the traceback went to a terminal nobody was watching -- leaving an
    admin nothing to debug with. The id ties the message on screen to the
    logged traceback."""
    error_id = uuid.uuid4().hex[:8]
    logger.exception("[%s] Unhandled error on %s %s", error_id, request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal error (reference {error_id}). See the backend log for details."},
    )


app.include_router(scan.router)
app.include_router(services.router)
app.include_router(scan_issues.router)
app.include_router(compatibility.router)
app.include_router(connections.router)
app.include_router(log_scan.router)
app.include_router(error_groups.router)
app.include_router(log_scan_issues.router)
app.include_router(adrs.router)
app.include_router(adr_issues.router)
app.include_router(dashboard.router)
app.include_router(filesystem.router)

# Serve the built frontend, if it has been built. Without this the only
# working configuration was "run the Vite dev server too", i.e. handing a
# company a dev server as their tool and a six-command install. Mounted
# last so it can never shadow an /api route, and skipped silently in
# development, where Vite serves the frontend itself and this directory
# does not exist.
_frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")
    logger.info("Serving the built frontend from %s", _frontend_dist)
else:
    logger.info("No built frontend found; run `npm run build` to serve it from here.")
