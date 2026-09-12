from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.analysis.version_compatibility import compute_compatibility, risks_for_service
from src.api.connections import ConnectionOut, build_adjacency
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


class ConflictingServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: int
    service_name: str
    declared_version: str | None


class CompatibilityRiskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    ecosystem: str
    declared_version: str | None
    conflicting_with: list[ConflictingServiceOut]


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
    compatibility_risks: list[CompatibilityRiskOut]
    connections: list[ConnectionOut]


@router.get("/services", response_model=list[ServiceSummary])
def list_services(session: Session = Depends(get_session)) -> list[Service]:
    return session.query(Service).order_by(Service.name).all()


@router.get("/services/{service_id}", response_model=ServiceDetail)
def get_service_detail(service_id: int, session: Session = Depends(get_session)) -> ServiceDetail:
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    # 002 US3: this service's own compatibility risks and connections,
    # reusing the same computations that back their dedicated views.
    risks = risks_for_service(compute_compatibility(session), service_id)
    node_entry = build_adjacency(session).get(("service", service_id))
    connections = node_entry.connections if node_entry is not None else []

    return ServiceDetail(
        id=service.id,
        name=service.name,
        ecosystem=service.ecosystem,
        repository_path=service.repository_path,
        manifest_path=service.manifest_path,
        is_complete=service.is_complete,
        last_scanned_at=service.last_scanned_at,
        dependencies=[DependencyOut.model_validate(dep) for dep in service.dependencies],
        compatibility_risks=[CompatibilityRiskOut.model_validate(risk) for risk in risks],
        connections=connections,
    )
