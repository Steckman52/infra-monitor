import logging
import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.db import get_session
from src.scanning.scan_service import run_scan

router = APIRouter(prefix="/api", tags=["scan"])
logger = logging.getLogger("infra_monitor.scan")

# Two overlapping registry scans used to both run to completion and replace
# each other's results, so whichever committed last silently won -- scan
# repo X in one tab and repo Y in another and one of them just vanished.
# One at a time, and the second caller is told so.
_scan_lock = threading.Lock()


class ScanRequest(BaseModel):
    roots: list[str]


class ScanResponse(BaseModel):
    services_found: int
    issues_found: int
    unreachable_roots: list[str]
    adrs_found: int


@router.post("/scan", response_model=ScanResponse)
def trigger_scan(request: ScanRequest, session: Session = Depends(get_session)) -> ScanResponse:
    if not _scan_lock.acquire(blocking=False):
        logger.warning("Registry scan rejected: another registry scan is running")
        raise HTTPException(
            status_code=409, detail="A registry scan is already running. Wait for it to finish."
        )
    logger.info("Registry scan starting over %d root(s): %s", len(request.roots), request.roots)
    try:
        summary = run_scan(session, request.roots)
    except OperationalError as exc:
        # The lock covers this process; a second process sharing the same
        # database file can still collide at the SQLite level.
        logger.warning("Registry scan rejected: another write is in progress")
        raise HTTPException(
            status_code=503, detail="Another scan is already in progress. Please try again shortly."
        ) from exc
    finally:
        _scan_lock.release()

    # The counts are what an admin needs when a user reports "it didn't find
    # my service" -- they say whether the scan reached the tree at all.
    logger.info(
        "Registry scan finished: %d services, %d issues, %d ADRs, %d unreachable root(s)",
        summary.services_found,
        summary.issues_found,
        summary.adrs_found,
        len(summary.unreachable_roots),
    )
    if summary.unreachable_roots:
        logger.warning("Unreachable roots: %s", summary.unreachable_roots)
    return ScanResponse(
        services_found=summary.services_found,
        issues_found=summary.issues_found,
        unreachable_roots=summary.unreachable_roots,
        adrs_found=summary.adrs_found,
    )
