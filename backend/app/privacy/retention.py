from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.governance import ProcessingLog

logger = logging.getLogger(__name__)


async def purge_expired_processing_logs(
    db: AsyncSession,
    retention_days: int = 365,
) -> int:
    """
    Purge processing_log entries older than statutory retention period (1 year under DPDP rules).
    """
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    res = await db.execute(
        delete(ProcessingLog).where(ProcessingLog.at < cutoff)
    )
    purged_count = res.rowcount or 0
    await db.commit()
    logger.info(f"Purged {purged_count} expired processing_log entries older than {cutoff}.")
    return purged_count
