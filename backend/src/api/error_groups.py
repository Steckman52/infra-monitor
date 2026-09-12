from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.error_group import ErrorGroup

router = APIRouter(prefix="/api", tags=["error-groups"])


class ErrorGroupSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int | None
    service_name: str | None
    unattributed_source_path: str | None
    normalized_template: str
    severity_marker: str
    occurrence_count: int
    first_seen: datetime | None
    last_seen: datetime | None


def _to_summary(group: ErrorGroup) -> ErrorGroupSummary:
    return ErrorGroupSummary(
        id=group.id,
        service_id=group.service_id,
        service_name=group.service.name if group.service else None,
        unattributed_source_path=group.unattributed_source_path,
        normalized_template=group.normalized_template,
        severity_marker=group.severity_marker,
        occurrence_count=group.occurrence_count,
        first_seen=group.first_seen,
        last_seen=group.last_seen,
    )


@router.get("/error-groups", response_model=list[ErrorGroupSummary])
def list_error_groups(session: Session = Depends(get_session)) -> list[ErrorGroupSummary]:
    groups = session.query(ErrorGroup).order_by(ErrorGroup.occurrence_count.desc()).all()
    return [_to_summary(group) for group in groups]
