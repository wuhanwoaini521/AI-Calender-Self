# AI Calendar 🗓️🤖

A smart calendar application with AI assistance, built with **Python FastAPI** backend and React frontend.

## 🚀 Quick Start

### Start the Python Backend

```bash
cd /mnt/okcomputer/output/app
./start_server.sh
```

Or manually:
```bash
cd /mnt/okcomputer/output/app/server
pip install -r requirements.txt
python run.py
```

The API will be available at `http://localhost:3001`

- API Documentation: http://localhost:3001/docs
- Health Check: http://localhost:3001/health

### Frontend

The frontend is already built and deployed. Access it at:
**https://6t2mbu77zgdgq.ok.kimi.link**

## 📁 Project Structure

```
/mnt/okcomputer/output/app/
├── server/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── core/             # Config & Security
│   │   │   ├── config.py     # Settings
│   │   │   └── security.py   # JWT & Password hashing
│   │   ├── models/           # Pydantic Models
│   │   │   ├── schemas.py    # Data models
│   │   │   └── database.py   # In-memory database
│   │   ├── routers/          # API Routes
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── events.py     # Calendar events
│   │   │   └── ai.py         # AI assistant
│   │   ├── services/         # Business Logic
│   │   │   └── ai_service.py # AI response generation
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt      # Python dependencies
│   └── run.py                # Entry point
├── dist/                     # Frontend (built)
│   └── index.html
└── start_server.sh           # Startup script
```

## 🛠️ Tech Stack

### Backend (Python)
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **dateutil** - Date/time handling

### Frontend
- React 18 (CDN)
- Tailwind CSS
- date-fns

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Events
- `GET /api/events` - List events (query: view, date)
- `POST /api/events` - Create event
- `GET /api/events/{id}` - Get event
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event
- `GET /api/events/upcoming` - Get upcoming events

### AI Assistant
- `POST /api/ai/chat` - Chat with AI
- `GET /api/ai/insights` - Get AI insights
- `PUT /api/ai/insights/{id}/read` - Mark insight as read
- `GET /api/ai/suggestions` - Get daily suggestions
- `POST /api/ai/schedule` - Generate optimized schedule

## ✨ Features

- 📅 **Multi-view Calendar**: Month, Week, Day views
- 📝 **Event Management**: Create, edit, delete events
- 🎨 **Color Coding**: 8 colors for event categories
- 🤖 **AI Assistant**: Smart scheduling suggestions
- 💬 **Natural Language**: Chat with AI about your schedule
- 🔐 **JWT Authentication**: Secure user sessions
- ⚡ **FastAPI**: High-performance async API

## 🔧 Configuration

Create `server/.env` file:
```env
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:5173
DEBUG=True
PORT=3001
```

## 🐍 Python Dependencies

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
python-dateutil==2.8.2
```

## 📄 License

MIT
