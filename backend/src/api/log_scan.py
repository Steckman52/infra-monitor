import logging
import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.db import get_session
from src.scanning.log_scan_service import run_log_scan

router = APIRouter(prefix="/api", tags=["log-scan"])
logger = logging.getLogger("infra_monitor.log_scan")

# Two overlapping log scans used to both run to completion and replace
# each other's results, so whichever committed last silently won -- scan
# repo X in one tab and repo Y in another and one of them just vanished.
# One at a time, and the second caller is told so.
_scan_lock = threading.Lock()


class LogScanRequest(BaseModel):
    root: str


class LogScanResponse(BaseModel):
    error_groups_found: int
    issues_found: int
    root_unreachable: bool


@router.post("/log-scan", response_model=LogScanResponse)
def trigger_log_scan(request: LogScanRequest, session: Session = Depends(get_session)) -> LogScanResponse:
    if not _scan_lock.acquire(blocking=False):
        logger.warning("Log scan rejected: another log scan is running")
        raise HTTPException(
            status_code=409, detail="A log scan is already running. Wait for it to finish."
        )
    logger.info("Log scan starting over %s", request.root)
    try:
        summary = run_log_scan(session, request.root)
    except OperationalError as exc:
        logger.warning("Log scan rejected: another write is in progress")
        raise HTTPException(
            status_code=503, detail="Another scan is already in progress. Please try again shortly."
        ) from exc
    finally:
        _scan_lock.release()

    logger.info(
        "Log scan finished: %d error groups, %d issues, root_unreachable=%s",
        summary.error_groups_found,
        summary.issues_found,
        summary.root_unreachable,
    )
    return LogScanResponse(
        error_groups_found=summary.error_groups_found,
        issues_found=summary.issues_found,
        root_unreachable=summary.root_unreachable,
    )
