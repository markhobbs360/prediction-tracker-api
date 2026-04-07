from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.feature import Feature
from app.models.intake_brief import IntakeBrief
from app.models.user import User
from app.schemas.intake import (
    DataReadinessResult,
    GateResult,
    IntakeCreate,
    IntakeOut,
    IntakeUpdate,
)
from app.services.audit_service import log_action
from app.services.gate_service import can_start_prediction
from app.services.score_service import compute_data_readiness

router = APIRouter(prefix="/intakes", tags=["intakes"])


@router.get("", response_model=list[IntakeOut])
async def list_intakes(
    client_id: UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(IntakeBrief)
    if client_id:
        stmt = stmt.where(IntakeBrief.client_id == client_id)
    if status_filter:
        stmt = stmt.where(IntakeBrief.status == status_filter)
    stmt = stmt.order_by(IntakeBrief.created_at.desc()).offset((page - 1) * 20).limit(20)
    result = await db.execute(stmt)
    return [IntakeOut.model_validate(i) for i in result.scalars().all()]


@router.post("", response_model=IntakeOut, status_code=status.HTTP_201_CREATED)
async def create_intake(
    body: IntakeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    intake = IntakeBrief(**body.model_dump(), created_by=user.id)
    db.add(intake)
    await db.flush()
    await db.refresh(intake)
    await log_action(db, "intake_brief", intake.id, "created", body.model_dump(), user.id)
    return IntakeOut.model_validate(intake)


@router.get("/{intake_id}", response_model=IntakeOut)
async def get_intake(
    intake_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    return IntakeOut.model_validate(intake)


@router.put("/{intake_id}", response_model=IntakeOut)
async def update_intake(
    intake_id: UUID,
    body: IntakeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    changes = body.model_dump(exclude_unset=True)
    for key, val in changes.items():
        setattr(intake, key, val)
    await db.flush()
    await db.refresh(intake)
    await log_action(db, "intake_brief", intake.id, "updated", changes, user.id)
    return IntakeOut.model_validate(intake)


@router.post("/{intake_id}/submit", response_model=IntakeOut)
async def submit_intake(
    intake_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    if intake.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft intakes can be submitted")

    # Compute data readiness before submission
    features_result = await db.execute(
        select(Feature).where(Feature.client_id == intake.client_id)
    )
    features = list(features_result.scalars().all())
    readiness = compute_data_readiness(intake, features)
    intake.data_readiness_score = readiness["score"]
    intake.data_readiness_detail = readiness["detail"]
    intake.status = "pending_review"

    await db.flush()
    await db.refresh(intake)
    await log_action(db, "intake_brief", intake.id, "submitted", {"data_readiness_score": readiness["score"]}, user.id)
    return IntakeOut.model_validate(intake)


@router.post("/{intake_id}/approve", response_model=IntakeOut)
async def approve_intake(
    intake_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    if intake.status != "pending_review":
        raise HTTPException(status_code=400, detail="Only submitted intakes can be approved")

    intake.status = "approved"
    intake.approved_by = user.id
    intake.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(intake)
    await log_action(db, "intake_brief", intake.id, "approved", None, user.id)
    return IntakeOut.model_validate(intake)


@router.post("/{intake_id}/reject", response_model=IntakeOut)
async def reject_intake(
    intake_id: UUID,
    reason: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    if intake.status != "pending_review":
        raise HTTPException(status_code=400, detail="Only submitted intakes can be rejected")

    intake.status = "rejected"
    intake.rejection_reason = reason
    await db.flush()
    await db.refresh(intake)
    await log_action(db, "intake_brief", intake.id, "rejected", {"reason": reason}, user.id)
    return IntakeOut.model_validate(intake)


@router.get("/{intake_id}/data-readiness", response_model=DataReadinessResult)
async def get_data_readiness(
    intake_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")

    features_result = await db.execute(
        select(Feature).where(Feature.client_id == intake.client_id)
    )
    features = list(features_result.scalars().all())
    readiness = compute_data_readiness(intake, features)
    return DataReadinessResult(score=readiness["score"], detail=readiness["detail"])


@router.get("/{intake_id}/gate-status", response_model=GateResult)
async def get_gate_status(
    intake_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")
    return can_start_prediction(intake)
