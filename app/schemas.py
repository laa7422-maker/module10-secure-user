from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator, Field


class UserCreate(BaseModel):
    """Schema for creating a new user. Used to validate incoming request data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None   # <-- ADDED
    password: str


class UserRead(BaseModel):
    """Schema for returning user data. Notice: no password or password_hash field here."""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None   # <-- ADDED
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating profile fields (PATCH-style). Only full_name is
    editable for now — username/email changes are intentionally excluded
    to keep identity fields stable."""
    full_name: Optional[str] = Field(default=None, max_length=100)


class PasswordChangeRequest(BaseModel):
    """Schema for changing an existing user's password."""
    current_password: str
    new_password: str

    @model_validator(mode="after")
    def validate_passwords_differ(self):
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
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
