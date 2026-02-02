import asyncpg


async def create_pg_pool(dsn: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn)
