from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    action: str,
    changes: dict | None = None,
    user_id: UUID | None = None,
) -> AuditLog:
    """Create an audit log entry."""
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes,
        performed_by=user_id,
    )
    db.add(entry)
    await db.flush()
    return entry
