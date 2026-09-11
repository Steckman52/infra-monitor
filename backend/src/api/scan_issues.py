from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.scan_issue import ScanIssue

router = APIRouter(prefix="/api", tags=["scan-issues"])


class ScanIssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manifest_path: str
    repository_path: str
    issue_type: str
    reason: str
    service_id: int | None
    detected_at: datetime


@router.get("/scan-issues", response_model=list[ScanIssueOut])
def list_scan_issues(session: Session = Depends(get_session)) -> list[ScanIssue]:
    return session.query(ScanIssue).order_by(ScanIssue.detected_at.desc()).all()
