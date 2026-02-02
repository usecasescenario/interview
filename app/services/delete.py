from uuid import UUID
import asyncpg
from fastapi import HTTPException


class DeletionService:
    def __init__(self, pg_pool: asyncpg.Pool):
        self.pg_pool: asyncpg.Pool = pg_pool

    async def queue_deletion(self, record_id: UUID):
        """Удаление строк из базы и индекса

        Удаляет строку из Postgres и добавляет её в очередь на удаление в outbox

        Args:
            record_id (UUID): uuid строки, подлежащей удалению
        """
        async with self.pg_pool.acquire() as conn:
            async with conn.transaction():
                # Проверяем, есть ли эта строка в Postgres
                # Если нет, возвращаем 404
                # Возвращаем удалённый id, чтобы убедиться, что строка удалена
                delete_query = "DELETE FROM vk WHERE id = $1 RETURNING id"
                deleted_id = await conn.fetchval(delete_query, record_id)

                if not deleted_id:
                    raise HTTPException(status_code=404, detail="Record not found")

                # Вставляем строку в outbox для удаления из Elasticsearch
                outbox_query = """
                    INSERT INTO outbox (payload, status, created_at)
                    VALUES ($1, 'pending', NOW())
                """
                # Сохраняем id и операцию в jsonb
                # Поле action сохраняет вид операции для упрощения расширения функционала
                payload: dict[str, str] = {
                    "action": "delete",
                    "index": "vk_index",
                    "id": str(record_id),
                }
                await conn.execute(outbox_query, payload)

        return True
