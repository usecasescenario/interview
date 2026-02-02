import asyncio
from datetime import datetime
import os
from ..settings import settings
from ..backfill_worker import backfill_vk


if __name__ == "__main__":
    cutoff_str: str = os.getenv("BACKFILL_CUTOFF", "2100-01-01T00:00:00")
    cutoff: datetime = datetime.fromisoformat(cutoff_str)

    asyncio.run(
        backfill_vk(
            pg_dsn=settings.PG_DSN,
            es_url=settings.ES_URL,
            index_name=settings.INDEX_NAME,
            cutoff=cutoff,
        )
    )
