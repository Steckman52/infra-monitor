from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
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
    try:
        summary = run_scan(session, request.roots)
    except OperationalError as exc:
        # SQLite serializes writers; a scan overlapping another one that's
        # still mid-transaction surfaces here instead of as a bare 500.
        raise HTTPException(
            status_code=503, detail="Another scan is already in progress. Please try again shortly."
        ) from exc
    return ScanResponse(
        services_found=summary.services_found,
        issues_found=summary.issues_found,
        unreachable_roots=summary.unreachable_roots,
        adrs_found=summary.adrs_found,
    )
