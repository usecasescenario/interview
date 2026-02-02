from fastapi import APIRouter, Depends, Query
from ..dependencies import search_service
from ..services.search import SearchService

router: APIRouter = APIRouter(prefix="/search")


@router.get("/")
async def execute_search(
    q: str = Query(..., min_length=1, description="Задавайте свои ответы"),
    limit: int = 20,
    # Помолимся
    service: SearchService = Depends(search_service),
):
    results = await service.search(query=q, limit=limit)
    return {"results": results}

