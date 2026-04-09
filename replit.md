# Star Collector

A mobile-first web application that helps users track progress toward personal goals through a gamified "star collection" system.

## Project Overview

Users set a target number of stars, track daily progress, reach milestones (25%, 50%, 75%), and earn rewards (e.g., "Movie Night", "Ice Cream").

## Architecture

- **Frontend**: Single HTML file (`StarCollector.html` / `index.html`) with embedded Tailwind CSS (CDN), Vanilla JS, and Material Symbols icons
- **Backend**: FastAPI (Python) on port 5000 — serves both the HTML frontend and the REST API (same origin, no CORS issues)
- **Database**: PostgreSQL (Replit built-in) — users table + star_data table
- **Auth**: JWT tokens (HS256, 7-day expiry), passwords hashed with bcrypt; token stored in localStorage as `starCollectorToken`
- **Storage**: Star data stored per-user in PostgreSQL; frontend uses relative API paths (`/auth/login`, `/data`, etc.)

## Project Structure

```
.
├── index.html              # Main app (copy of StarCollector.html for web serving)
├── StarCollector.html      # Original source HTML
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI app with all routes
│   ├── auth.py             # JWT + bcrypt password helpers
│   ├── database.py         # PostgreSQL connection helpers
│   └── run.py              # Uvicorn entrypoint
├── pages/
│   └── picturebook/
│       └── CHANGELOG.md    # Chinese development log / feature spec
└── replit.md               # This file
```

## Running the App

One workflow runs everything:

| Workflow | Command | Port |
|---|---|---|
| Start application | `python3 -m backend.run` | 5000 (frontend + API) |

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register new user, returns JWT |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/data` | Bearer token | Get current user's star data |
| PUT | `/data` | Bearer token | Save current user's star data |
| GET | `/health` | No | Health check |

## Database Schema

```sql
users (id SERIAL PK, username VARCHAR UNIQUE, password_hash TEXT, created_at TIMESTAMP)
star_data (id SERIAL PK, user_id INTEGER FK → users, data JSONB, updated_at TIMESTAMP)
```

## Star Data JSON Shape

```json
{
  "totalStars": 0,
  "monthlyStars": 0,
  "lastMonth": 3,
  "goal": 200,
  "milestones": { "completed": [], "total": [25, 50, 75] },
  "checkins": ["2026-04-09"],
  "reward": "",
  "customReward": ""
}
```

## Key Features

- **Star tracking**: Tap to add a star toward a user-defined goal
- **Milestones**: Visual celebrations at 25%, 50%, and 75% progress
- **Calendar**: Daily check-in tracking and monthly check-in counter
- **Rewards**: Preset or custom reward selection for goal completion
- **Month summary**: Stars earned this month displayed on home screen
- **Accounts**: Real user registration/login with per-account data isolation
