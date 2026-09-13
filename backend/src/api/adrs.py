from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.adr_record import AdrRecord
from src.models.adr_relationship import AdrRelationship
from src.models.adr_service_association import AdrServiceAssociation

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


class RelatedAdr(BaseModel):
    adr_id: int
    title: str


class RelatedService(BaseModel):
    service_id: int
    service_name: str


class AdrDetail(AdrSummary):
    content: str
    supersedes: list[RelatedAdr]
    superseded_by: list[RelatedAdr]
    amends: list[RelatedAdr]
    amended_by: list[RelatedAdr]
    related_services: list[RelatedService]


@router.get("/adrs", response_model=list[AdrSummary])
def list_adrs(session: Session = Depends(get_session)) -> list[AdrRecord]:
    return session.query(AdrRecord).order_by(AdrRecord.title).all()


@router.get("/adrs/{adr_id}", response_model=AdrDetail)
def get_adr_detail(adr_id: int, session: Session = Depends(get_session)) -> AdrDetail:
    adr = session.get(AdrRecord, adr_id)
    if adr is None:
        raise HTTPException(status_code=404, detail="ADR not found")

    outgoing = session.query(AdrRelationship).filter(AdrRelationship.from_adr_id == adr_id).all()
    incoming = session.query(AdrRelationship).filter(AdrRelationship.to_adr_id == adr_id).all()
    associations = (
        session.query(AdrServiceAssociation).filter(AdrServiceAssociation.adr_id == adr_id).all()
    )

    return AdrDetail(
        id=adr.id,
        title=adr.title,
        normalized_status=adr.normalized_status,
        raw_status=adr.raw_status,
        date=adr.date,
        source_path=adr.source_path,
        has_secret_warning=adr.has_secret_warning,
        content=adr.content,
        supersedes=[
            RelatedAdr(adr_id=r.to_adr_id, title=r.to_adr.title)
            for r in outgoing
            if r.relationship_type == "supersedes"
        ],
        superseded_by=[
            RelatedAdr(adr_id=r.from_adr_id, title=r.from_adr.title)
            for r in incoming
            if r.relationship_type == "supersedes"
        ],
        amends=[
            RelatedAdr(adr_id=r.to_adr_id, title=r.to_adr.title)
            for r in outgoing
            if r.relationship_type == "amends"
        ],
        amended_by=[
            RelatedAdr(adr_id=r.from_adr_id, title=r.from_adr.title)
            for r in incoming
            if r.relationship_type == "amends"
        ],
        related_services=[
            RelatedService(service_id=a.service_id, service_name=a.service.name)
            for a in associations
        ],
    )
