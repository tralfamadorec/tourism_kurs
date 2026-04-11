from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class AttractionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, description="Название достопримечательности")
    description: Optional[str] = Field(None, description="Описание объекта")
    address: Optional[str] = Field(None, description="Физический адрес")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Широта (WGS84)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Долгота (WGS84)")
    photo_url: Optional[str] = Field(None, description="Ссылка на изображение")

class AttractionCreate(AttractionBase):
    pass

class AttractionResponse(AttractionBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)