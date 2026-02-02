from datetime import datetime
import asyncio
import aiohttp
import asyncpg
from elasticsearch import AsyncElasticsearch, helpers
import os


BATCH_SIZE = 500


async def backfill_vk(
    pg_dsn: str,
    es_url: str,
    index_name: str,
    cutoff: datetime,
) -> None:
    """
    Backfill для заполнения Elasticsearch'а.
    Имплементация относительно наивная.
    При ошибке или перезапуске state не сохраняется.

    Args:
        pg_dsn (str): Адрес Postgres
        es_url (str): Адрес Elasticsearch
        index_name (str): Название индекса в Elasticsearch
        cutoff (datetime): Дата и время, данные до которых внесены

    """
    # BUG: С каждым перезапуском количество загружаемых строк заметно увеличивается
    # Это видно по количеству выводимых "Проиндексировано N строк"
    pg = await asyncpg.connect(pg_dsn)
    es: AsyncElasticsearch = AsyncElasticsearch(es_url)

    last_created = datetime.min
    last_id = "00000000-0000-0000-0000-000000000000"

    try:
        while True:
            rows = await pg.fetch(
                """
                SELECT id, text, created_date
                FROM vk
                WHERE created_date <= $1
                  AND (created_date, id) > ($2, $3)
                ORDER BY created_date, id
                LIMIT $4
                """,
                cutoff,
                last_created,
                last_id,
                BATCH_SIZE,
            )

            if not rows:
                print("Backfill завершён")
                return

            actions = []
            for row in rows:
                actions.append(
                    {
                        "_op_type": "index",
                        "_index": index_name,
                        "_id": str(row["id"]),
                        "_source": {
                            "id": str(row["id"]),
                            "text": row["text"],
                        },
                    }
                )

            success, errors = await helpers.async_bulk(
                es, actions, raise_on_error=False
            )

            if errors:
                raise RuntimeError(errors)
            last_created = rows[-1]["created_date"]
            last_id = rows[-1]["id"]

            print(f"Проиндексированы {success} строк")

    finally:
        await es.close()
        await pg.close()


if __name__ == "__main__":
    cutoff_str: str = os.getenv("BACKFILL_CUTOFF", "2100-01-01T00:00:00")
    cutoff: datetime = datetime.fromisoformat(cutoff_str)

    # TODO: Сделать импорт дефолтных настроек из settings
    asyncio.run(
        backfill_vk(
            pg_dsn=os.environ["PG_DSN"],
            es_url=os.environ["ES_URL"],
            index_name=os.environ["INDEX_NAME"],
            cutoff=cutoff,
        )
    )
