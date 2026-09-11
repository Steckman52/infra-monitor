from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.service import Service

router = APIRouter(prefix="/api", tags=["services"])


class ServiceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ecosystem: str
    repository_path: str
    is_complete: bool


@router.get("/services", response_model=list[ServiceSummary])
def list_services(session: Session = Depends(get_session)) -> list[Service]:
    return session.query(Service).order_by(Service.name).all()
