from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
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


class ErrorOccurrenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_text: str
    occurred_at: datetime | None
    source_log_path: str
    line_number: int


class ErrorGroupDetail(ErrorGroupSummary):
    example_text: str
    occurrences: list[ErrorOccurrenceOut]


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


@router.get("/error-groups/{group_id}", response_model=ErrorGroupDetail)
def get_error_group_detail(group_id: int, session: Session = Depends(get_session)) -> ErrorGroupDetail:
    group = session.get(ErrorGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Error group not found")

    summary = _to_summary(group)
    return ErrorGroupDetail(
        **summary.model_dump(),
        example_text=group.example_text,
        occurrences=[ErrorOccurrenceOut.model_validate(o) for o in group.occurrences],
    )
