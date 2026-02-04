# AI Calendar - Agent Development Guide

This document provides essential information for AI coding agents working on the AI Calendar project.

## Project Overview

AI Calendar is a smart calendar application with AI assistance capabilities. It features a React-based frontend and a Python FastAPI backend.

**Key Features:**
- Multi-view calendar (Month, Week, Day)
- Event management with color coding
- AI-powered scheduling assistant
- JWT-based authentication
- Smart scheduling suggestions and conflict detection

## Technology Stack

### Frontend
- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS 3.4 with CSS Variables
- **UI Components:** shadcn/ui (New York style) + Radix UI primitives
- **State Management:** React hooks (useState, useContext)
- **HTTP Client:** Native fetch API
- **Date Handling:** date-fns
- **Form Handling:** react-hook-form + Zod validation
- **Toast Notifications:** sonner
- **Icons:** lucide-react

### Backend
- **Framework:** FastAPI 0.109.0
- **Server:** Uvicorn 0.27.0
- **Authentication:** JWT (python-jose) + bcrypt (passlib)
- **Data Validation:** Pydantic 2.5.3 + pydantic-settings
- **Date/Time:** python-dateutil
- **Database:** In-memory (Python dictionaries)

## Project Structure

```
app/
├── src/                          # Frontend source code
│   ├── App.tsx                   # Main application component
│   ├── main.tsx                  # React entry point
│   ├── index.css                 # Global styles + Tailwind
│   ├── App.css                   # App-specific styles
│   ├── ai/                       # AI-related components
│   │   └── AIAssistant.tsx       # AI chat interface
│   ├── calendar/                 # Calendar view components
│   │   ├── MonthView.tsx
│   │   ├── WeekView.tsx
│   │   ├── DayView.tsx
│   │   └── EventDialog.tsx       # Create/edit event modal
│   ├── components/               # Shared components
│   │   ├── AuthDialog.tsx        # Login/register modal
│   │   ├── Header.tsx            # App header with nav
│   │   └── ui/                   # shadcn/ui components (50+ files)
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.ts            # Authentication context
│   │   ├── useCalendar.ts        # Calendar data fetching
│   │   ├── useAI.ts              # AI assistant hook
│   │   └── use-mobile.ts         # Mobile detection
│   ├── lib/                      # Utility functions
│   │   └── utils.ts              # cn() helper for Tailwind
│   ├── services/                 # API services
│   │   └── api.ts                # ApiService class
│   └── types/                    # TypeScript definitions
│       └── index.ts              # All type definitions
├── server/                       # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── __init__.py
│   │   ├── core/                 # Core modules
│   │   │   ├── config.py         # Settings & configuration
│   │   │   └── security.py       # JWT & password hashing
│   │   ├── models/               # Data models
│   │   │   ├── schemas.py        # Pydantic models
│   │   │   └── database.py       # In-memory database
│   │   ├── routers/              # API routes
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── events.py         # Event CRUD endpoints
│   │   │   └── ai.py             # AI assistant endpoints
│   │   └── services/             # Business logic
│   │       └── ai_service.py     # AI response generation
│   ├── run.py                    # Server entry point
│   └── requirements.txt          # Python dependencies
├── dist/                         # Frontend build output
├── package.json                  # NPM dependencies
├── vite.config.ts                # Vite configuration
├── tailwind.config.js            # Tailwind configuration
├── tsconfig.json                 # TypeScript configuration
└── components.json               # shadcn/ui configuration
```

## Build & Development Commands

### Frontend (from project root)

```bash
# Install dependencies
npm install

# Start development server (port 5173)
npm run dev

# Build for production (outputs to dist/)
npm run build

# Preview production build
npm run preview

# Run ESLint
npm run lint
```

### Backend (from server/ directory)

```bash
# Start the server (using uv)
./start_server.sh

# Or manually
cd server
pip install -r requirements.txt
python run.py

# The API will be available at http://localhost:3001
# API Documentation: http://localhost:3001/docs
```

## Configuration

### Frontend Environment Variables
- `VITE_API_URL` - Backend API URL (default: http://localhost:3001/api)

### Backend Environment Variables (server/.env)
```env
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:5173
DEBUG=True
PORT=3001
```

## Code Style Guidelines

### TypeScript/React
- Use functional components with hooks
- Props interfaces should be defined inline or in types/
- Use the `cn()` utility for conditional Tailwind classes
- Follow shadcn/ui patterns for UI components
- Use `@/` path alias for imports from src/

### Python
- Follow PEP 8 style guidelines
- Use type hints where possible
- Use Pydantic models for request/response validation
- Organize imports: stdlib → third-party → local

### Naming Conventions
- **Components:** PascalCase (e.g., `EventDialog.tsx`)
- **Hooks:** camelCase with `use` prefix (e.g., `useCalendar.ts`)
- **Utilities:** camelCase (e.g., `utils.ts`)
- **Types/Interfaces:** PascalCase (e.g., `CalendarEvent`)
- **Python files:** snake_case (e.g., `ai_service.py`)

## API Endpoints

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

## Key Implementation Details

### Authentication Flow
1. User logs in via `/api/auth/login`
2. Backend returns JWT token + user data
3. Token is stored in localStorage
4. Token is sent in `Authorization: Bearer <token>` header for protected routes
5. `useAuth` hook manages authentication state

### Calendar Data Flow
1. `useCalendar` hook fetches events based on current view and date
2. Events are passed to view components (MonthView, WeekView, DayView)
3. User interactions trigger API calls via `api` service
4. After mutations, `refreshEvents()` is called to update UI

### AI Assistant
- Rule-based AI service (no ML model required)
- Responds to keywords for scheduling queries
- Detects conflicts, suggests free time slots
- Provides productivity tips and meeting optimization

### Database (In-Memory)
- `Database` class in `server/app/models/database.py`
- Uses Python dictionaries for storage
- Data is lost on server restart (by design for demo)
- Supports users, events, insights, and chat messages

## Testing

Currently, the project does not have automated tests. When adding tests:

### Frontend Testing
- Use Vitest for unit tests
- Use React Testing Library for component tests
- Test files: `*.test.ts` or `*.test.tsx`

### Backend Testing
- Use pytest for Python tests
- FastAPI provides `TestClient` for API testing

## Security Considerations

1. **JWT Tokens:** Tokens expire after 7 days (configurable in settings)
2. **CORS:** Configured to allow only specific frontend origins
3. **Password Hashing:** Uses bcrypt via passlib
4. **Input Validation:** All inputs validated via Pydantic schemas
5. **No HTTPS:** Development only - use HTTPS in production

## Common Tasks

### Adding a New API Endpoint

1. Add route handler in appropriate router (server/app/routers/)
2. Update Pydantic schemas if needed (server/app/models/schemas.py)
3. Add corresponding method in ApiService (src/services/api.ts)
4. Create/update hook for data fetching (src/hooks/)

### Adding a New UI Component

1. Check if component exists in shadcn/ui registry
2. Use `npx shadcn add <component>` to add
3. Customize as needed in `src/components/ui/`
4. Follow existing patterns for props and styling

### Modifying the Database Schema

1. Update Pydantic models in `server/app/models/schemas.py`
2. Update database operations in `server/app/models/database.py`
3. Update corresponding TypeScript types in `src/types/index.ts`
4. Update API service methods in `src/services/api.ts`

## Deployment Notes

- Frontend builds to static files in `dist/`
- Backend serves API on configured port
- For production, set `DEBUG=False` and use strong `SECRET_KEY`
- Consider replacing in-memory database with real database for production

## Important File Locations

| Purpose | Path |
|---------|------|
| Frontend entry | `src/main.tsx` |
| Main App component | `src/App.tsx` |
| API base URL | `src/services/api.ts` |
| All types | `src/types/index.ts` |
| Backend entry | `server/run.py` |
| FastAPI app | `server/app/main.py` |
| Database instance | `server/app/models/database.py` |
| AI logic | `server/app/services/ai_service.py` |
| Tailwind config | `tailwind.config.js` |
| Vite config | `vite.config.ts` |
