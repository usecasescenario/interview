from pathlib import Path
import asyncpg
import asyncio
import os

BASE_DIR: Path = Path(__file__).resolve().parent
SQL_DIR: Path = BASE_DIR / "sql"


async def run_sql_file(conn, filename: str):
    sql = (SQL_DIR / filename).read_text()
    await conn.execute(sql)


async def ingest():
    conn = await asyncpg.connect(os.getenv("PG_DSN"))

    async with conn.transaction():
        await run_sql_file(conn, "001_staging.sql")

        # Копируем CSV при помощи COPY, т.к. это быстро и надёжно
        with open("data/source.csv", "rb") as f:
            # Исходим из того, что в CSV есть заголовки
            await conn.copy_to_table("vk_staging", columns=("text", "created_date", "rubrics_raw"), source=f, format="csv", header=True)


        await run_sql_file(conn, "002_vk.sql")
        await run_sql_file(conn, "003_rubrics.sql")
        await run_sql_file(conn, "004_outbox.sql")

        # Чистим vk_staging, чтобы не добавлять уже имеющиеся строки
        await conn.execute("TRUNCATE TABLE vk_staging")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(ingest())
