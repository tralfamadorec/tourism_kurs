from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class AccommodationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    rating: Optional[float] = Field(None, ge=0, le=5)
    price_per_night: Optional[int] = Field(None, ge=0)
    is_accessible: Optional[bool] = False 
    photo_url: Optional[str] = None

class AccommodationCreate(AccommodationBase): 
    pass

class AccommodationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    price_per_night: Optional[int] = None
    is_accessible: Optional[bool] = None 
    photo_url: Optional[str] = None

class AccommodationResponse(AccommodationBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class AttractionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, description="Название достопримечательности")
    description: Optional[str] = Field(None, description="Описание объекта")
    address: Optional[str] = Field(None, description="Физический адрес")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Широта (WGS84)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Долгота (WGS84)")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Рейтинг")
    is_accessible: Optional[bool] = False 
    photo_url: Optional[str] = Field(None, description="Ссылка на изображение")

class AttractionCreate(AttractionBase):
    pass

class AttractionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    is_accessible: Optional[bool] = None 
    photo_url: Optional[str] = None

class AttractionResponse(AttractionBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_accessible: Optional[bool] = False 
    photo_url: Optional[str] = None

class EventCreate(EventBase): 
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_accessible: Optional[bool] = None 
    photo_url: Optional[str] = None

class EventResponse(EventBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class FoodBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    cuisine: Optional[str] = None
    avg_price: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    photo_url: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_accessible: Optional[bool] = False 

class FoodCreate(FoodBase): 
    pass

class FoodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    cuisine: Optional[str] = None
    avg_price: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_accessible: Optional[bool] = None

class FoodResponse(FoodBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PostcardTemplateBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    image_url: str
    description: Optional[str] = None

class PostcardTemplateCreate(PostcardTemplateBase):
    pass

class PostcardTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    image_url: Optional[str] = None
    description: Optional[str] = None

class PostcardTemplateResponse(PostcardTemplateBase):
    id: int
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)

class RouteBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    duration_hours: Optional[float] = Field(None, ge=0.5)
    difficulty: Optional[str] = Field(None, max_length=50)
    transport_type: Optional[str] = Field(None, max_length=50)
    is_accessible: Optional[bool] = False 
    photo_url: Optional[str] = None

class RouteCreate(RouteBase): 
    pass

class RouteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    difficulty: Optional[str] = None
    transport_type: Optional[str] = None
    is_accessible: Optional[bool] = None 
    photo_url: Optional[str] = None

class RouteResponse(RouteBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class SafetyObjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = None
    phone: str = Field(..., min_length=1, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_accessible: Optional[bool] = False
    photo_url: Optional[str] = None

class SafetyObjectCreate(SafetyObjectBase): 
    pass

class SafetyObjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=2, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_accessible: Optional[bool] = None
    photo_url: Optional[str] = None

class SafetyObjectResponse(SafetyObjectBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SouvenirBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None  # Тип магазина
    working_hours: Optional[str] = None  # Режим работы
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_accessible: Optional[bool] = False
    photo_url: Optional[str] = None

class SouvenirCreate(SouvenirBase): 
    pass

class SouvenirUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    working_hours: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_accessible: Optional[bool] = None
    photo_url: Optional[str] = None

class SouvenirResponse(SouvenirBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

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

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int