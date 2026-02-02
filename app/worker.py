import asyncio
import json
import logging
from typing import Optional
from asyncpg.pool import Pool
from elasticsearch import AsyncElasticsearch, NotFoundError
import asyncpg
from app.settings import settings

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger("outbox-worker")


class OutboxWorker:
    def __init__(self, es: AsyncElasticsearch, pool: Pool):
        self.es: AsyncElasticsearch = es
        self.pool: Optional[Pool] = pool

    async def connect(self):
        self.pool: asyncpg.pool.Pool = await asyncpg.create_pool(dsn=settings.PG_DSN)

    async def process_tasks(self):
        async with self.pool.acquire() as conn:
            # Получаем и закрепляем за процессом конкретные строки,
            # Чтобы после не возникало ошибок
            # При этом пропускаем уже закреплённые строки, чтобы не было конфликтов

            async with conn.transaction():
                tasks = await conn.fetch("""
                    SELECT id, payload 
                    FROM outbox 
                    WHERE status = 'pending' 
                    FOR UPDATE SKIP LOCKED
                    LIMIT 10
                """)

                for task in tasks:
                    task_id = task["id"]
                    payload = json.loads(task["payload"])

                    try:
                        if payload["action"] == "delete":
                            await self.delete_from_es(payload["index"], payload["id"])

                        # Помечаем строки как обработанные
                        # NB: помимо pending и processed состояний есть failed
                        await conn.execute(
                            "UPDATE outbox SET status = 'processed', processed_at = NOW() WHERE id = $1",
                            task_id,
                        )
                        logger.info(
                            f"Выполнена задача {task_id}, удалено: {payload['id']}"
                        )

                    except Exception as e:
                        logger.error(f"Не удалось выполнить задачу {task_id}: {e}")

    async def delete_from_es(self, index: str, doc_id: str):
        try:
            await self.es.delete(index=index, id=doc_id)
        except NotFoundError:
            # Если строки в Elasticsearch'е уже нет, то выводим уведомление
            # После этого идём дальше
            logger.warning(f"Строка {doc_id} уже удалена из elasticsearch.")
        except Exception as e:
            raise e

    async def run(self):
        await self.connect()
        logger.info("Процесс запущен. Ожидает задачи")
        try:
            while True:
                await self.process_tasks()
                # Проверяем, есть ли новые строки раз в 5 секунд
                await asyncio.sleep(5)
        finally:
            await self.es.close()
            await self.pool.close() # Pool is closed due to AIDS, lmao


if __name__ == "__main__":
    worker: OutboxWorker = OutboxWorker()
    asyncio.run(worker.run())
