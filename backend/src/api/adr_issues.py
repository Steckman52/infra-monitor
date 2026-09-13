from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.adr_import_issue import AdrImportIssue
from src.models.adr_record import AdrRecord
from src.scanning.adr_secrets import describe_secret_warning

router = APIRouter(prefix="/api", tags=["adr-issues"])


class AdrIssue(BaseModel):
    type: str
    path: str
    reason: str
    adr_id: int | None = None


@router.get("/adr-issues", response_model=list[AdrIssue])
def list_adr_issues(session: Session = Depends(get_session)) -> list[AdrIssue]:
    """Combines parse failures and secret warnings from the most recent
    scan into one view (data-model.md Notes / FR-011) -- two genuinely
    different sources, not a single merged table."""
    parse_failures = [
        AdrIssue(type="parse_failure", path=issue.path, reason=issue.reason)
        for issue in session.query(AdrImportIssue).all()
    ]
    flagged_records = session.query(AdrRecord).filter(AdrRecord.has_secret_warning.is_(True)).all()
    secret_warnings = [
        AdrIssue(
            type="secret_warning",
            path=record.source_path,
            reason=describe_secret_warning(record.content) or "Content resembles a secret",
            adr_id=record.id,
        )
        for record in flagged_records
    ]
    return parse_failures + secret_warnings
