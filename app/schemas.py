from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator


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


class CalculationType(str, Enum):
    add = "Add"
    sub = "Sub"
    multiply = "Multiply"
    divide = "Divide"


class CalculationCreate(BaseModel):
    """Schema for creating a new calculation. Validates operands and type."""
    a: float
    b: float
    type: CalculationType

    @model_validator(mode="after")
    def validate_no_zero_divisor(self):
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationUpdate(BaseModel):
    """Schema for editing an existing calculation. All fields optional
    to support partial updates (PATCH-style edits)."""
    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[CalculationType] = None

    @model_validator(mode="after")
    def validate_no_zero_divisor(self):
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    """Schema for returning calculation data, including the computed result."""
    id: int
    a: float
    b: float
    type: CalculationType
    result: Optional[float] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
