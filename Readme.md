# SpeakU 🗣️
> A Language Exchange API where users practice languages with native speakers via real-time voice calls.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-lightblue)](https://supabase.com)

## 🌟 What is SpeakU?
SpeakU connects language learners with native speakers for real-time voice practice.
- A Hindi speaker wanting to learn English gets matched with an English speaker wanting to learn Hindi
- They have a voice call via Agora SDK
- After the call, they rate each other
- They earn Lingos (credits) for quality conversations

## 🏗️ Architecture
```
Client → FastAPI → PostgreSQL (Supabase)
           ↓
        WebSocket → In-memory Matchmaking Queue
           ↓
        Agora SDK → Voice Call
```

## 🚀 Tech Stack
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API + WebSocket |
| PostgreSQL | Database (Supabase) |
| SQLAlchemy | ORM |
| JWT | Authentication |
| WebSocket | Real-time Matchmaking |
| Agora SDK | Voice Calls |
| Bcrypt | Password Hashing |
| Redis | Production Queue (Upstash) |

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login + get JWT token |

### Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile/me` | Get my profile |
| PUT | `/profile/language` | Set native + learning language |

### Matchmaking (WebSocket)
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/match/find?token=JWT` | Find a language partner |

### Calls
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calls/token` | Get Agora voice call token |
| POST | `/calls/end` | End call + earn Lingos |
| POST | `/calls/rate` | Rate your partner (1-5 stars) |
| GET | `/calls/lingos` | Check Lingos balance |

## 🔄 User Flow
```
Register → Set Language → Find Match (WebSocket)
    → Voice Call (Agora) → Rate Partner → Earn Lingos
```

## 💡 Key Features
- **JWT Authentication** — Stateless, secure
- **Real-time Matchmaking** — WebSocket based
- **Smart Matching Algorithm** — Complementary language pairs
- **Voice Calls** — Agora SDK (10,000 free minutes/month)
- **Lingos System** — Credit economy for balanced exchange
- **Rating System** — Quality control with bonus credits

## 🗄️ Database Schema
```
users          → id, username, email, native_language, learning_language, lingos
call_sessions  → id, caller_id, receiver_id, agora_channel, duration
call_ratings   → id, call_session_id, rater_id, rated_id, rating, feedback
```

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/deepakpandey2004/SpeakU.git
cd SpeakU
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup .env file
```env
DATABASE_URL=your_supabase_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
AGORA_APP_ID=your_agora_app_id
AGORA_APP_CERTIFICATE=your_agora_certificate
REDIS_URL=your_upstash_redis_url
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open API docs
```
http://127.0.0.1:8000/docs
```

## 🧪 Testing
Test with Postman or Swagger UI at `/docs`

### WebSocket Matchmaking Test:
1. Open two Postman WebSocket tabs
2. Connect both with different user tokens
3. Watch real-time matching happen!

## 📊 Lingos Economy
- 🎁 **50 Lingos** on signup
- ⏱️ **1 Lingo** per minute of call
- ⭐ **5 Bonus Lingos** for 4-5 star rating received

## 🔮 Future Improvements
- [ ] Redis for distributed matchmaking
- [ ] Text chat during calls
- [ ] Language proficiency levels
- [ ] Weekly leaderboard
- [ ] Mobile app integration

## 👨‍💻 Author
**Deepak Pandey**
- GitHub: [@deepakpandey2004](https://github.com/deepakpandey2004)