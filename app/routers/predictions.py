from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.intake_brief import IntakeBrief
from app.models.prediction import Prediction, PredictionVersion
from app.models.user import User
from app.schemas.prediction import (
    PredictionCreate,
    PredictionOut,
    PredictionUpdate,
    PredictionVersionCreate,
    PredictionVersionOut,
)
from app.schemas.intake import GateResult
from app.services.audit_service import log_action
from app.services.gate_service import can_start_prediction

router = APIRouter(tags=["predictions"])


@router.post(
    "/intakes/{intake_id}/predictions",
    response_model=PredictionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_prediction(
    intake_id: UUID,
    body: PredictionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(IntakeBrief).where(IntakeBrief.id == intake_id))
    intake = result.scalar_one_or_none()
    if intake is None:
        raise HTTPException(status_code=404, detail="Intake brief not found")

    # Enforce gate
    gate = can_start_prediction(intake)
    if not gate.can_proceed:
        failed = [c.message for c in gate.checks if not c.passed]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Gate check failed: {'; '.join(failed)}",
        )

    prediction = Prediction(
        intake_brief_id=intake.id,
        client_id=intake.client_id,
        flowers_prediction_url=body.flowers_prediction_url,
        notes=body.notes,
        created_by=user.id,
    )
    db.add(prediction)
    await db.flush()

    # Create initial version
    version_data = body.version.model_dump() if body.version else {}
    version = PredictionVersion(
        prediction_id=prediction.id,
        version_number=1,
        created_by=user.id,
        **version_data,
    )
    db.add(version)
    await db.flush()
    await db.refresh(prediction)

    await log_action(db, "prediction", prediction.id, "created", None, user.id)
    return PredictionOut.model_validate(prediction)


@router.get("/predictions", response_model=list[PredictionOut])
async def list_predictions(
    client_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from fastapi import Query as Q
    stmt = select(Prediction)
    if client_id:
        stmt = stmt.where(Prediction.client_id == client_id)
    stmt = stmt.order_by(Prediction.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    return [PredictionOut.model_validate(p) for p in result.scalars().all()]


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
async def get_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return PredictionOut.model_validate(prediction)


@router.put("/predictions/{prediction_id}", response_model=PredictionOut)
async def update_prediction(
    prediction_id: UUID,
    body: PredictionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    changes = body.model_dump(exclude_unset=True)
    for key, val in changes.items():
        setattr(prediction, key, val)
    await db.flush()
    await db.refresh(prediction)
    await log_action(db, "prediction", prediction.id, "updated", changes, user.id)
    return PredictionOut.model_validate(prediction)


@router.post("/predictions/{prediction_id}/start", response_model=PredictionOut)
async def start_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if prediction.status not in ("queued", "paused"):
        raise HTTPException(status_code=400, detail="Prediction cannot be started from current status")

    prediction.status = "in_progress"

    # Mark current version started
    ver_result = await db.execute(
        select(PredictionVersion).where(
            PredictionVersion.prediction_id == prediction.id,
            PredictionVersion.version_number == prediction.current_version,
        )
    )
    version = ver_result.scalar_one_or_none()
    if version and version.started_at is None:
        version.started_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(prediction)
    await log_action(db, "prediction", prediction.id, "started", None, user.id)
    return PredictionOut.model_validate(prediction)


@router.post("/predictions/{prediction_id}/complete", response_model=PredictionOut)
async def complete_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if prediction.status != "in_progress":
        raise HTTPException(status_code=400, detail="Only in-progress predictions can be completed")

    prediction.status = "completed"

    ver_result = await db.execute(
        select(PredictionVersion).where(
            PredictionVersion.prediction_id == prediction.id,
            PredictionVersion.version_number == prediction.current_version,
        )
    )
    version = ver_result.scalar_one_or_none()
    if version and version.completed_at is None:
        version.completed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(prediction)
    await log_action(db, "prediction", prediction.id, "completed", None, user.id)
    return PredictionOut.model_validate(prediction)


@router.post("/predictions/{prediction_id}/new-version", response_model=PredictionVersionOut)
async def new_version(
    prediction_id: UUID,
    body: PredictionVersionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    new_num = prediction.current_version + 1
    version = PredictionVersion(
        prediction_id=prediction.id,
        version_number=new_num,
        created_by=user.id,
        **body.model_dump(),
    )
    db.add(version)
    prediction.current_version = new_num
    prediction.status = "queued"
    await db.flush()
    await db.refresh(version)
    await log_action(db, "prediction", prediction.id, "new_version", {"version_number": new_num}, user.id)
    return PredictionVersionOut.model_validate(version)


@router.get("/predictions/{prediction_id}/versions", response_model=list[PredictionVersionOut])
async def list_versions(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = (
        select(PredictionVersion)
        .where(PredictionVersion.prediction_id == prediction_id)
        .order_by(PredictionVersion.version_number)
    )
    result = await db.execute(stmt)
    return [PredictionVersionOut.model_validate(v) for v in result.scalars().all()]
