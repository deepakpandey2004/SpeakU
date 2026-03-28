from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, LanguageUpdate
from app.auth import get_current_user_swagger

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user_swagger)):
    return current_user

@router.put("/language", response_model=UserResponse)
def update_language(
    language: LanguageUpdate,
    current_user: User = Depends(get_current_user_swagger),
    db: Session = Depends(get_db)
):
    if language.native_language == language.learning_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Native and learning language cannot be same!"
        )
    current_user.native_language = language.native_language
    current_user.learning_language = language.learning_language
    db.commit()
    db.refresh(current_user)
    return current_user
