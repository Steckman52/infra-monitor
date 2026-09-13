from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.analysis.version_compatibility import compute_compatibility, risks_for_service
from src.api.connections import ConnectionOut, build_adjacency
from src.api.error_groups import ErrorGroupSummary, to_summary as error_group_to_summary
from src.db import get_session
from src.models.adr_service_association import AdrServiceAssociation
from src.models.error_group import ErrorGroup
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


class RelatedAdrOut(BaseModel):
    adr_id: int
    title: str


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
    related_adrs: list[RelatedAdrOut]
    recent_error_groups: list[ErrorGroupSummary]


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

    # Polish round: pull in what the ADR module and log analysis already
    # know about this same service, so its own detail page doesn't require
    # a separate trip through each feature's own screen.
    associations = (
        session.query(AdrServiceAssociation).filter(AdrServiceAssociation.service_id == service_id).all()
    )
    related_adrs = [RelatedAdrOut(adr_id=a.adr_id, title=a.adr.title) for a in associations]
    error_groups = (
        session.query(ErrorGroup)
        .filter(ErrorGroup.service_id == service_id)
        .order_by(ErrorGroup.occurrence_count.desc())
        .all()
    )
    recent_error_groups = [error_group_to_summary(group) for group in error_groups]

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
        related_adrs=related_adrs,
        recent_error_groups=recent_error_groups,
    )
