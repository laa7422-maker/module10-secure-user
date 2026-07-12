from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user. Used to validate incoming request data."""
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Schema for returning user data. Notice: no password or password_hash field here."""
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
