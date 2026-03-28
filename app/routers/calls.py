from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, CallSession, CallRating
from app.schemas import (
    CallTokenRequest, CallTokenResponse,
    CallEndRequest, RatingRequest, LingosResponse
)
from app.auth import get_current_user_swagger
from dotenv import load_dotenv
import os
import time

load_dotenv()

router = APIRouter(prefix="/calls", tags=["Calls"])

def generate_agora_token(channel: str, uid: int) -> str:
    """Agora token generate karta hai"""
    try:
        from agora_token_builder import RtcTokenBuilder, Role_Publisher
        app_id = os.getenv("AGORA_APP_ID")
        app_certificate = os.getenv("AGORA_APP_CERTIFICATE")
        expire_time = 3600  # 1 hour
        current_time = int(time.time())
        privilege_expire_time = current_time + expire_time
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel, uid,
            Role_Publisher, privilege_expire_time
        )
        return token
    except Exception as e:
        # Fallback — test ke liye
        return f"test_token_{channel}_{uid}"


@router.post("/token", response_model=CallTokenResponse)
def get_call_token(
    request: CallTokenRequest,
    current_user: User = Depends(get_current_user_swagger),
    db: Session = Depends(get_db)
):
    """Agora voice call token generate karo"""
    
    app_id = os.getenv("AGORA_APP_ID")
    token = generate_agora_token(request.channel, request.uid or current_user.id)
    
    # Call session database mein save karo
    # Channel se dono users find karo
    parts = request.channel.replace("speaku_", "").split("_")
    if len(parts) == 2:
        user1_id, user2_id = int(parts[0]), int(parts[1])
        other_user_id = user2_id if current_user.id == user1_id else user1_id
        
        # Check karo session already exists kya
        existing = db.query(CallSession).filter(
            CallSession.agora_channel == request.channel
        ).first()
        
        if not existing:
            call_session = CallSession(
                caller_id=current_user.id,
                receiver_id=other_user_id,
                agora_channel=request.channel
            )
            db.add(call_session)
            db.commit()
    
    return {
        "token": token,
        "channel": request.channel,
        "app_id": app_id
    }


@router.post("/end")
def end_call(
    request: CallEndRequest,
    current_user: User = Depends(get_current_user_swagger),
    db: Session = Depends(get_db)
):
    """Call end karo aur duration save karo"""
    from datetime import datetime, timezone
    
    # Call session find karo
    call_session = db.query(CallSession).filter(
        CallSession.agora_channel == request.channel
    ).first()
    
    if not call_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call session not found"
        )
    
    # Duration save karo
    call_session.ended_at = datetime.now(timezone.utc)
    call_session.duration_seconds = request.duration_seconds
    
    # Lingos system
    # 1 minute = 1 lingo earn + 1 lingo spend
    minutes = max(1, request.duration_seconds // 60)
    lingos_earned = minutes
    
    # Caller ko lingos milenge
    caller = db.query(User).filter(User.id == call_session.caller_id).first()
    receiver = db.query(User).filter(User.id == call_session.receiver_id).first()
    
    if caller:
        caller.lingos += lingos_earned
    if receiver:
        receiver.lingos += lingos_earned
    
    db.commit()
    
    return {
        "message": "Call ended successfully!",
        "duration_seconds": request.duration_seconds,
        "lingos_earned": lingos_earned,
        "your_lingos": current_user.lingos + lingos_earned
    }


@router.post("/rate")
def rate_user(
    request: RatingRequest,
    current_user: User = Depends(get_current_user_swagger),
    db: Session = Depends(get_db)
):
    """Call ke baad dusre user ko rate karo"""
    
    # Rating 1-5 check karo
    if not 1 <= request.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Apne aap ko rate nahi kar sakte
    if request.rated_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate yourself!"
        )
    
    # Call session find karo
    call_session = db.query(CallSession).filter(
        CallSession.agora_channel == request.channel
    ).first()
    
    if not call_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call session not found"
        )
    
    # Check karo pehle rate kiya kya
    existing_rating = db.query(CallRating).filter(
        CallRating.call_session_id == call_session.id,
        CallRating.rater_id == current_user.id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this call!"
        )
    
    # Rating save karo
    rating = CallRating(
        call_session_id=call_session.id,
        rater_id=current_user.id,
        rated_id=request.rated_user_id,
        rating=request.rating,
        feedback=request.feedback
    )
    db.add(rating)
    
    # Bonus lingos for good rating
    if request.rating >= 4:
        rated_user = db.query(User).filter(User.id == request.rated_user_id).first()
        if rated_user:
            rated_user.lingos += 5  # 5 bonus lingos for 4-5 star rating
    
    db.commit()
    
    return {
        "message": "Rating submitted successfully!",
        "rating": request.rating,
        "feedback": request.feedback
    }


@router.get("/lingos", response_model=LingosResponse)
def get_lingos(
    current_user: User = Depends(get_current_user_swagger)
):
    """Apna Lingos balance dekho"""
    return {
        "username": current_user.username,
        "lingos": current_user.lingos
    }