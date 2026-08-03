import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False) # <--- ADDED THIS LINE
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Secret(Base):
    __tablename__ = "secrets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    
    # SRID 4326 is standard GPS coordinates (Latitude/Longitude)
    location = Column(Geometry(geometry_type='POINT', srid=4326, spatial_index=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Nullable means it can be left blank (for permanent premium drops)
    expires_at = Column(DateTime(timezone=True), nullable=True) 

class Discovery(Base):
    __tablename__ = "discoveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    secret_id = Column(String, ForeignKey("secrets.id"))
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())