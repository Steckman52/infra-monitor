from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_session
from src.scanning.log_scan_service import run_log_scan

router = APIRouter(prefix="/api", tags=["log-scan"])


class LogScanRequest(BaseModel):
    root: str


class LogScanResponse(BaseModel):
    error_groups_found: int
    issues_found: int


@router.post("/log-scan", response_model=LogScanResponse)
def trigger_log_scan(request: LogScanRequest, session: Session = Depends(get_session)) -> LogScanResponse:
    summary = run_log_scan(session, request.root)
    return LogScanResponse(
        error_groups_found=summary.error_groups_found,
        issues_found=summary.issues_found,
    )
