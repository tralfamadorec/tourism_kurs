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

class AttractionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6, max_length=128)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)