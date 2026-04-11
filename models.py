from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from database import Base

class Attraction(Base):
    __tablename__="attractions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String, nullable=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo_url = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="created_attractions")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    def __repr__(self):
        return f"<Attraction(id={self.id}, name='{self.name}')>"
    
class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_attractions = relationship("Attraction", back_populates="creator")
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"    