from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os, json
from app.config import settings
from app.database import engine, Base
from app.core.websocket import manager
from app.core.security import decode_token

# Load all models before routers so SQLAlchemy registers every table once
import app.models.user      # noqa: F401
import app.models.challenge  # noqa: F401
import app.models.project    # noqa: F401
import app.models.learning   # noqa: F401

from app.routers import auth, users, challenges, projects, learning, mentorship, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create upload dirs
    os.makedirs(f"{settings.UPLOAD_DIR}/avatars", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/documents", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/project-files", exist_ok=True)
    # Create DB tables (Alembic handles migrations in production)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Discover Rwanda API",
    description="""
## Discover Rwanda Platform API

Connects ALU students with Africa's tourism technology challenges.

### User Roles
- **Student** — browse challenges, join teams, build portfolio
- **Tourism Business** — post challenges, collaborate with student teams
- **Faculty/Staff** — advise students, manage team assignments
- **Admin** — manage platform, review challenges, analytics

### Authentication
All endpoints (except /auth/register and /auth/login) require a Bearer JWT token.
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(challenges.router)
app.include_router(projects.router)
app.include_router(learning.router)
app.include_router(mentorship.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── WebSocket: real-time project chat ─────────────────────────────────────────

@app.websocket("/ws/projects/{project_id}")
async def project_ws(
    websocket: WebSocket,
    project_id: int,
    token: str = Query(...),
):
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
        user_name = payload.get("name", f"User {user_id}")
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, project_id, user_id, user_name)

    # Notify others
    await manager.broadcast_to_project(project_id, {
        "type": "user_joined",
        "user_id": user_id,
        "user_name": user_name,
        "online_users": manager.get_online_users(project_id),
    }, exclude_ws=websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            # Broadcast message to all project members
            await manager.broadcast_to_project(project_id, {
                "type": "message",
                "user_id": user_id,
                "user_name": user_name,
                "content": msg.get("content", ""),
                "message_type": msg.get("message_type", "text"),
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        await manager.broadcast_to_project(project_id, {
            "type": "user_left",
            "user_id": user_id,
            "user_name": user_name,
            "online_users": manager.get_online_users(project_id),
        })