import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .database import get_connection, get_cursor
from .auth import hash_password, verify_password, create_access_token, decode_token


class _Bearer401(HTTPBearer):
    async def __call__(self, request: Request):
        try:
            return await super().__call__(request)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )


INIT_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS star_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS star_data_user_id_idx ON star_data(user_id);
"""

DEFAULT_STAR_DATA = {
    "totalStars": 0,
    "monthlyStars": 0,
    "lastMonth": None,
    "goal": 200,
    "milestones": {"completed": [], "total": [25, 50, 75]},
    "checkins": [],
    "reward": "",
    "customReward": "",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(INIT_SQL)
        conn.commit()
    finally:
        conn.close()
    yield


app = FastAPI(title="Star Collector API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = _Bearer401()


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return int(user_id)


@app.post("/auth/register")
def register(req: RegisterRequest):
    username = req.username.strip()
    if not username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    if len(username) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Username already exists")

            password_hash = hash_password(req.password)
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (username, password_hash),
            )
            user = cur.fetchone()
            user_id = user["id"]

            import datetime
            current_month = datetime.datetime.now().month - 1
            initial_data = {**DEFAULT_STAR_DATA, "lastMonth": current_month}
            cur.execute(
                "INSERT INTO star_data (user_id, data) VALUES (%s, %s)",
                (user_id, json.dumps(initial_data)),
            )
            conn.commit()

        token = create_access_token({"sub": str(user_id), "username": username})
        return {"access_token": token, "token_type": "bearer", "username": username}
    finally:
        conn.close()


@app.post("/auth/login")
def login(req: LoginRequest):
    username = req.username.strip()
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if not user or not verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_access_token({"sub": str(user["id"]), "username": username})
        return {"access_token": token, "token_type": "bearer", "username": username}
    finally:
        conn.close()


@app.get("/data")
def get_data(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT data FROM star_data WHERE user_id = %s", (user_id,))
            row = cur.fetchone()

        if not row:
            return DEFAULT_STAR_DATA
        return row["data"]
    finally:
        conn.close()


@app.put("/data")
def put_data(payload: dict, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                INSERT INTO star_data (user_id, data, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET data = EXCLUDED.data, updated_at = NOW()
                """,
                (user_id, json.dumps(payload)),
            )
            conn.commit()
        return {"success": True}
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/StarCollector.html", response_class=HTMLResponse)
def serve_star_collector():
    with open("StarCollector.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/", response_class=HTMLResponse)
def serve_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())
