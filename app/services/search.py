from elasticsearch import AsyncElasticsearch
import asyncpg
from ..settings import settings


# Так как в Elasticsearch'е должны лежать только id и text,
# Мы используем его лишь для поиска. Потом получаем от него id
# И забираем нужные строки из Postgres.
# Главное, чтобы удалённые в одной базе строки были удалены и в другой.
# А то беда.


class SearchService:
    def __init__(self, es: AsyncElasticsearch, pg_pool: asyncpg.Pool):
        self.es: AsyncElasticsearch = es
        self.pg_pool: asyncpg.Pool = pg_pool

    async def search(self, query: str, limit: int = 20):
        overfetch: int = limit * 3

        # Поиск по Elasticsearch'у
        resp = await self.es.search(
            index=settings.INDEX_NAME,
            body={
                "query": {"match": {"text": query}},
                "_source": False,
                "size": overfetch,
            },
        )
        # Ответы из Elasticsearch'а приходят в json.
        # Нас здесь инересует только hits, в которых лежат результаты
        # hits тоже приходят в json, и в них нас интересует только _id
        es_ids: list[str] = [hit["_id"] for hit in resp["hits"]["hits"]]

        if not es_ids:
            return []

        # Подтягиваем данные из Postgres'а
        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM vk
                WHERE id = ANY($1)
                ORDER BY created_date DESC
                LIMIT $2
                """,
                es_ids,
                limit,
            )

        return [
            {
                "id": str(r["id"]),
                "text": r["text"],
                "created_date": r["created_date"].isoformat(),
            }
            for r in rows
        ]

