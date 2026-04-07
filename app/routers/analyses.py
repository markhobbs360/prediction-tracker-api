from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisOut, AnalysisUpdate
from app.schemas.intake import GateResult
from app.services.audit_service import log_action
from app.services.gate_service import can_deliver_analysis

router = APIRouter(tags=["analyses"])


@router.post(
    "/predictions/{prediction_id}/analyses",
    response_model=AnalysisOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_analysis(
    prediction_id: UUID,
    body: AnalysisCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    analysis = Analysis(
        prediction_id=prediction.id,
        client_id=prediction.client_id,
        created_by=user.id,
        **body.model_dump(),
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    await log_action(db, "analysis", analysis.id, "created", None, user.id)
    return AnalysisOut.model_validate(analysis)


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return AnalysisOut.model_validate(analysis)


@router.put("/analyses/{analysis_id}", response_model=AnalysisOut)
async def update_analysis(
    analysis_id: UUID,
    body: AnalysisUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    changes = body.model_dump(exclude_unset=True)
    for key, val in changes.items():
        setattr(analysis, key, val)
    await db.flush()
    await db.refresh(analysis)
    await log_action(db, "analysis", analysis.id, "updated", changes, user.id)
    return AnalysisOut.model_validate(analysis)


@router.post("/analyses/{analysis_id}/deliver", response_model=AnalysisOut)
async def deliver_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    gate = can_deliver_analysis(analysis)
    if not gate.can_proceed:
        failed = [c.message for c in gate.checks if not c.passed]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Delivery gate check failed: {'; '.join(failed)}",
        )

    analysis.status = "delivered"
    analysis.delivered_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(analysis)
    await log_action(db, "analysis", analysis.id, "delivered", None, user.id)
    return AnalysisOut.model_validate(analysis)


@router.get("/analyses/{analysis_id}/gate-status", response_model=GateResult)
async def get_analysis_gate_status(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return can_deliver_analysis(analysis)
