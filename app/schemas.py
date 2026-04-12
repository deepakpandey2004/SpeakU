from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

# JWT Token response
class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    native_language: Optional[str]
    learning_language: Optional[str]
    lingos: int

    class Config:
        from_attributes = True


    

class LanguageUpdate(BaseModel):
    native_language: str
    learning_language: str

# Call token request
class CallTokenRequest(BaseModel):
    channel: str
    uid: int = 0


class CallTokenResponse(BaseModel):
    token: str
    channel: str
    app_id: str


class CallEndRequest(BaseModel):
    channel: str
    duration_seconds: int


class RatingRequest(BaseModel):
    channel: str
    rated_user_id: int
    rating: int  # 1-5
    feedback: Optional[str] = None


class LingosResponse(BaseModel):
    username: str
    lingos: int
