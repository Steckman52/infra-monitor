from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.adr_record import AdrRecord

router = APIRouter(prefix="/api", tags=["adrs"])


class AdrSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    normalized_status: str
    raw_status: str | None
    date: date | None
    source_path: str
    has_secret_warning: bool


@router.get("/adrs", response_model=list[AdrSummary])
def list_adrs(session: Session = Depends(get_session)) -> list[AdrRecord]:
    return session.query(AdrRecord).order_by(AdrRecord.title).all()
