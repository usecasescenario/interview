from fastapi import APIRouter, Depends, Query
from ..schema import DeleteResponse
from ..dependencies import deletion_service
from ..services.delete import DeletionService
from uuid import UUID

router: APIRouter = APIRouter(prefix="/vk")


@router.delete("/{id}", response_model=DeleteResponse)
async def delete_vk_record(
    id: UUID, service: DeletionService = Depends(deletion_service)
):
    await service.queue_deletion(id)
    return {"id": id}
