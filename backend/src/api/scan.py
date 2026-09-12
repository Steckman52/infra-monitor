from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_session
from src.scanning.scan_service import run_scan

router = APIRouter(prefix="/api", tags=["scan"])


class ScanRequest(BaseModel):
    roots: list[str]


class ScanResponse(BaseModel):
    services_found: int
    issues_found: int
    unreachable_roots: list[str]
    adrs_found: int


@router.post("/scan", response_model=ScanResponse)
def trigger_scan(request: ScanRequest, session: Session = Depends(get_session)) -> ScanResponse:
    summary = run_scan(session, request.roots)
    return ScanResponse(
        services_found=summary.services_found,
        issues_found=summary.issues_found,
        unreachable_roots=summary.unreachable_roots,
        adrs_found=summary.adrs_found,
    )
