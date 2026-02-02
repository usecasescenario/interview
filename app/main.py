import asyncio
from contextlib import asynccontextmanager
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Depends, Request
from asyncpg import Pool
from fastapi.routing import APIRoute


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.settings import settings
    from app.db import create_pg_pool
    from app.es import create_es_client
    from app.worker import OutboxWorker
    app.state.pg_pool = await create_pg_pool(settings.PG_DSN)
    app.state.es = create_es_client(settings.ES_URL)
    worker: OutboxWorker = OutboxWorker(es=app.state.es, pool=app.state.pg_pool)
    worker_task = asyncio.create_task(worker.run())
    yield

    worker_task.cancel()
    await app.state.pg_pool.close()
    await app.state.es.close()


app: FastAPI = FastAPI(lifespan=lifespan)

from app.routes.search import router as search_router
from app.routes.delete import router as delete_router

app.include_router(search_router)
app.include_router(delete_router)
