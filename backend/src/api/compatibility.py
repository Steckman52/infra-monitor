from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.analysis.version_compatibility import CompatibilityGroup, compute_compatibility
from src.db import get_session

router = APIRouter(prefix="/api", tags=["compatibility"])


class CompatibilityEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: int
    service_name: str
    declared_version: str | None
    major_version: int | None


class CompatibilityGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    ecosystem: str
    status: str
    has_not_comparable: bool
    entries: list[CompatibilityEntryOut]


@router.get("/dependency-compatibility", response_model=list[CompatibilityGroupOut])
def list_compatibility(session: Session = Depends(get_session)) -> list[CompatibilityGroup]:
    return compute_compatibility(session)
