from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
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


class DependencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    declared_version: str | None


class ServiceDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ecosystem: str
    repository_path: str
    manifest_path: str
    is_complete: bool
    last_scanned_at: datetime
    dependencies: list[DependencyOut]


@router.get("/services", response_model=list[ServiceSummary])
def list_services(session: Session = Depends(get_session)) -> list[Service]:
    return session.query(Service).order_by(Service.name).all()


@router.get("/services/{service_id}", response_model=ServiceDetail)
def get_service_detail(service_id: int, session: Session = Depends(get_session)) -> Service:
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
