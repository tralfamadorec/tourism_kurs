from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

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
    photo_url: Optional[str] = None

class AccommodationCreate(AccommodationBase): 
    pass

class AccommodationUpdate(AccommodationBase):
    name: Optional[str] = Field(None, min_length=3, max_length=255)

class AccommodationResponse(AccommodationBase):
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
    photo_url: Optional[str] = None

class EventCreate(EventBase): 
    pass

class EventUpdate(EventBase):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    event_date: Optional[datetime] = None

class EventResponse(EventBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    cuisine: Optional[str] = None
    avg_price: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    photo_url: Optional[str] = None

class RestaurantCreate(RestaurantBase): 
    pass

class RestaurantUpdate(RestaurantBase):
    name: Optional[str] = Field(None, min_length=3, max_length=255)

class RestaurantResponse(RestaurantBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class RouteBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    duration_hours: Optional[float] = Field(None, ge=0.5)
    difficulty: Optional[str] = Field(None, max_length=50)
    transport_type: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = None

class RouteCreate(RouteBase): 
    pass

class RouteUpdate(RouteBase):
    title: Optional[str] = Field(None, min_length=3, max_length=255)

class RouteResponse(RouteBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int

class SouvenirBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    producer: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    photo_url: Optional[str] = None

class SouvenirCreate(SouvenirBase): 
    pass

class SouvenirUpdate(SouvenirBase):
    name: Optional[str] = Field(None, min_length=2, max_length=255)

class SouvenirResponse(SouvenirBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class SafetyObjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., min_length=2, max_length=50)
    address: Optional[str] = None
    phone: str = Field(..., min_length=5, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SafetyObjectCreate(SafetyObjectBase): 
    pass

class SafetyObjectResponse(SafetyObjectBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PostcardTemplateBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    image_url: str
    description: Optional[str] = None

class PostcardTemplateResponse(PostcardTemplateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)