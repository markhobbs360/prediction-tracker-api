from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.feedback import FeedbackEntry
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackUpdate

router = APIRouter(tags=["feedback"])


@router.get("/analyses/{analysis_id}/feedback", response_model=list[FeedbackOut])
async def list_feedback_for_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(FeedbackEntry).where(FeedbackEntry.analysis_id == analysis_id)
    result = await db.execute(stmt)
    return [FeedbackOut.model_validate(f) for f in result.scalars().all()]


@router.post(
    "/analyses/{analysis_id}/feedback",
    response_model=FeedbackOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    analysis_id: UUID,
    body: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    entry = FeedbackEntry(
        analysis_id=analysis.id,
        client_id=analysis.client_id,
        recorded_by=user.id,
        **body.model_dump(),
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return FeedbackOut.model_validate(entry)


@router.put("/feedback/{feedback_id}", response_model=FeedbackOut)
async def update_feedback(
    feedback_id: UUID,
    body: FeedbackUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(FeedbackEntry).where(FeedbackEntry.id == feedback_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Feedback entry not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(entry, key, val)
    await db.flush()
    await db.refresh(entry)
    return FeedbackOut.model_validate(entry)


@router.get("/clients/{client_id}/feedback", response_model=list[FeedbackOut])
async def list_feedback_for_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = (
        select(FeedbackEntry)
        .where(FeedbackEntry.client_id == client_id)
        .order_by(FeedbackEntry.created_at.desc())
    )
    result = await db.execute(stmt)
    return [FeedbackOut.model_validate(f) for f in result.scalars().all()]
