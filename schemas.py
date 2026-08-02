from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SecretCreate(BaseModel):
    creator_id: str
    message: str
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")
    expires_at: Optional[datetime] = None  # Leave null for permanent premium drops

class UserCreate(BaseModel):
    id: str
    username: str
    email: str