import json
from typing import Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import AuditLog


async def record_audit(
    session: AsyncSession,
    action: str,
    actor_user_id: Optional[uuid.UUID] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    session.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=json.dumps(metadata, default=str) if metadata else None,
        )
    )
