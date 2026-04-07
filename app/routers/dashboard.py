from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.audit_log import CrossClientInsight
from app.models.client import Client
from app.models.feedback import FeedbackEntry
from app.models.intake_brief import IntakeBrief
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.dashboard import (
    CrossClientInsightOut,
    DashboardSummary,
    PipelineItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    total_clients = (
        await db.execute(select(func.count(Client.id)).where(Client.is_active.is_(True)))
    ).scalar_one()

    active_intakes = (
        await db.execute(
            select(func.count(IntakeBrief.id)).where(
                IntakeBrief.status.in_(["draft", "submitted", "approved"])
            )
        )
    ).scalar_one()

    predictions_in_progress = (
        await db.execute(
            select(func.count(Prediction.id)).where(
                Prediction.status.in_(["queued", "in_progress"])
            )
        )
    ).scalar_one()

    analyses_delivered = (
        await db.execute(
            select(func.count(Analysis.id)).where(Analysis.status == "delivered")
        )
    ).scalar_one()

    # Analyses that are delivered but have no feedback yet
    delivered_ids_stmt = select(Analysis.id).where(Analysis.status == "delivered")
    has_feedback_stmt = select(FeedbackEntry.analysis_id).distinct()
    pending_feedback = (
        await db.execute(
            select(func.count(Analysis.id)).where(
                Analysis.status == "delivered",
                Analysis.id.not_in(has_feedback_stmt),
            )
        )
    ).scalar_one()

    return DashboardSummary(
        total_clients=total_clients,
        active_intakes=active_intakes,
        predictions_in_progress=predictions_in_progress,
        analyses_delivered=analyses_delivered,
        pending_feedback=pending_feedback,
    )


@router.get("/pipeline", response_model=list[PipelineItem])
async def get_pipeline(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    items: list[PipelineItem] = []

    # Active intakes
    intake_stmt = (
        select(IntakeBrief)
        .where(IntakeBrief.status.in_(["draft", "submitted", "approved"]))
        .order_by(IntakeBrief.updated_at.desc())
        .limit(50)
    )
    intakes = (await db.execute(intake_stmt)).scalars().all()
    for intake in intakes:
        client_name = intake.client.name if intake.client else "Unknown"
        items.append(
            PipelineItem(
                id=intake.id,
                title=intake.title,
                client_name=client_name,
                stage="intake",
                status=intake.status,
                updated_at=intake.updated_at,
            )
        )

    # Active predictions
    pred_stmt = (
        select(Prediction)
        .where(Prediction.status.in_(["queued", "in_progress"]))
        .order_by(Prediction.updated_at.desc())
        .limit(50)
    )
    predictions = (await db.execute(pred_stmt)).scalars().all()
    for pred in predictions:
        client_name = pred.client.name if pred.client else "Unknown"
        title = pred.intake_brief.title if pred.intake_brief else f"Prediction {pred.id}"
        items.append(
            PipelineItem(
                id=pred.id,
                title=title,
                client_name=client_name,
                stage="prediction",
                status=pred.status,
                updated_at=pred.updated_at,
            )
        )

    # Active analyses
    analysis_stmt = (
        select(Analysis)
        .where(Analysis.status.in_(["draft", "internal_review", "client_ready"]))
        .order_by(Analysis.updated_at.desc())
        .limit(50)
    )
    analyses = (await db.execute(analysis_stmt)).scalars().all()
    for analysis in analyses:
        client_name = analysis.client.name if analysis.client else "Unknown"
        items.append(
            PipelineItem(
                id=analysis.id,
                title=analysis.title,
                client_name=client_name,
                stage="analysis",
                status=analysis.status,
                updated_at=analysis.updated_at,
            )
        )

    items.sort(key=lambda x: x.updated_at, reverse=True)
    return items


@router.get("/cross-client-insights", response_model=list[CrossClientInsightOut])
async def get_cross_client_insights(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(CrossClientInsight).order_by(CrossClientInsight.created_at.desc()).limit(50)
    result = await db.execute(stmt)
    return [CrossClientInsightOut.model_validate(i) for i in result.scalars().all()]
