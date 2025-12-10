# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Auth
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_admin: Optional[bool] = False

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True  # pydantic v2 migration (was orm_mode)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Offense input
class PlayInput(BaseModel):
    down: int
    ydstogo: int
    yrdline100: int
    qtr: int
    ScoreDiff: float

# Defense input
class DefenseRequest(BaseModel):
    down: int
    ydstogo: int
    yardline_100: int
    qtr: int
    score_differential: int
    quarter_seconds_remaining: int







