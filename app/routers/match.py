from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_token
import json
import asyncio

router = APIRouter(prefix="/match", tags=["Matchmaking"])


waiting_users = {}  

@router.websocket("/find")
async def find_match(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    await websocket.accept()

    
    payload = verify_token(token)
    if not payload:
        await websocket.send_json({"status": "error", "message": "Invalid token"})
        await websocket.close()
        return

    from app.models import User
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        await websocket.send_json({"status": "error", "message": "User not found"})
        await websocket.close()
        return

    if not user.native_language or not user.learning_language:
        await websocket.send_json({
            "status": "error",
            "message": "Please set your languages first!"
        })
        await websocket.close()
        return

    my_key = f"{user.native_language}:{user.learning_language}"
    opposite_key = f"{user.learning_language}:{user.native_language}"

    user_data = {
        "user_id": user.id,
        "username": user.username,
        "native_language": user.native_language,
        "learning_language": user.learning_language
    }

    await websocket.send_json({
        "status": "searching",
        "message": f"Looking for a {user.learning_language} speaker..."
    })

    
    if opposite_key in waiting_users and len(waiting_users[opposite_key]) > 0:
        
        waiting_user_data, waiting_ws = waiting_users[opposite_key].pop(0)
        
        channel = f"speaku_{min(user_id, waiting_user_data['user_id'])}_{max(user_id, waiting_user_data['user_id'])}"

        
        await websocket.send_json({
            "status": "matched",
            "message": "Match found! 🎉",
            "channel": channel,
            "matched_with": waiting_user_data['username'],
            "their_language": waiting_user_data['native_language']
        })

        
        try:
            await waiting_ws.send_json({
                "status": "matched",
                "message": "Match found! 🎉",
                "channel": channel,
                "matched_with": user.username,
                "their_language": user.native_language
            })
        except:
            pass

        await websocket.close()

    else:
        
        if my_key not in waiting_users:
            waiting_users[my_key] = []
        
        waiting_users[my_key].append((user_data, websocket))

        await websocket.send_json({
            "status": "waiting",
            "message": "Waiting for a match... (up to 60 seconds)"
        })

        
        try:
            await asyncio.sleep(60)
            
            if my_key in waiting_users:
                waiting_users[my_key] = [
                    (u, ws) for u, ws in waiting_users[my_key]
                    if u['user_id'] != user_id
                ]
            await websocket.send_json({
                "status": "timeout",
                "message": "No match found. Please try again!"
            })
        except WebSocketDisconnect:
            
            if my_key in waiting_users:
                waiting_users[my_key] = [
                    (u, ws) for u, ws in waiting_users[my_key]
                    if u['user_id'] != user_id
                ]
