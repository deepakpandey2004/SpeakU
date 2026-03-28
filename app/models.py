from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    native_language = Column(String, nullable=True)
    learning_language = Column(String, nullable=True)
    lingos = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ratings_given = relationship("CallRating", foreign_keys="CallRating.rater_id", back_populates="rater")
    ratings_received = relationship("CallRating", foreign_keys="CallRating.rated_id", back_populates="rated")

class CallSession(Base):
    __tablename__ = "call_sessions"
    id = Column(Integer, primary_key=True, index=True)
    caller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agora_channel = Column(String, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    caller = relationship("User", foreign_keys=[caller_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    ratings = relationship("CallRating", back_populates="call_session")

class CallRating(Base):
    __tablename__ = "call_ratings"
    id = Column(Integer, primary_key=True, index=True)
    call_session_id = Column(Integer, ForeignKey("call_sessions.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    call_session = relationship("CallSession", back_populates="ratings")
    rater = relationship("User", foreign_keys=[rater_id], back_populates="ratings_given")
    rated = relationship("User", foreign_keys=[rated_id], back_populates="ratings_received")