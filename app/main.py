from fastapi import FastAPI
from app.database import engine, Base
from app.models import User, CallSession, CallRating
from app.routers import users, profile, match, calls

app = FastAPI(
    title="SpeakU",
    description="Language Exchange Voice Call API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(profile.router)
app.include_router(match.router)
app.include_router(calls.router)

@app.get("/")
def root():
    return {"message": "Welcome to SpeakU API!"}