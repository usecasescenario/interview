from fastapi import Request
from .services.search import SearchService
from .services.delete import DeletionService


def search_service(request: Request) -> SearchService:
    return SearchService(es=request.app.state.es, pg_pool=request.app.state.pg_pool)


def deletion_service(request: Request) -> DeletionService:
    return DeletionService(pg_pool=request.app.state.pg_pool)
