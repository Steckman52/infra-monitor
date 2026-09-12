from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.log_scan_issue import LogScanIssue

router = APIRouter(prefix="/api", tags=["log-scan-issues"])


class LogScanIssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    path: str
    issue_type: str
    reason: str
    detected_at: datetime


@router.get("/log-scan-issues", response_model=list[LogScanIssueOut])
def list_log_scan_issues(session: Session = Depends(get_session)) -> list[LogScanIssue]:
    return session.query(LogScanIssue).order_by(LogScanIssue.detected_at.desc()).all()
