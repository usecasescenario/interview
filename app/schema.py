from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Any


# Базовая модель для всех данных
class VKBase(BaseModel):
    text: str
    created_date: datetime
    rubrics: dict[str, Any]


# Схема для чтения данных
class VKRecord(VKBase):
    id: UUID  # Позволяет автоматически конвертировать uuid в строку и обратно

    # Благодаря этому Pydantic читает данные, даже если это Record
    model_config = ConfigDict(from_attributes=True)


# Обёртка над результатами поиска
class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[VKRecord]


# Подтверждение факта удаления
class DeleteResponse(BaseModel):
    id: UUID
    status: str = "queued"
    message: str = "Удаление поставлено в очередь"
