"""
ATHLETIX — FastAPI Backend Entry Point
backend/app/main.py

Main application bootstrap and routing registry for the ATHLETIX platform.

Key Architecture Responsibilities:
- Lifecycle Management: Initializes background processes (including the real-time AI Streamlit gym coach)
  and handles clean application shutdown.
- Middleware Configuration: Configures Cross-Origin Resource Sharing (CORS) across development and
  production environments.
- Exception Handling: Intercepts HTTP and unhandled internal exceptions to return secure, structured JSON responses.
- Router Registration: Mounts all modular API route handlers under the '/api/v1' versioned prefix.
- Health Monitoring: Exposes the '/health' endpoint for container orchestrators and uptime checks.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import (
    auth,
    users,
    videos,
    assessments,
    leaderboard,
    verifications,
    shortlists,
    notifications,
    admin,
    live_coach,
    push_tokens,
)

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("athletix")


def start_streamlit_coach_background():
    """
    Spawns the Streamlit AI Gym Coach background engine on port 8501 if not already running.
    This enables real-time interactive webcam workout analysis.
    """
    try:
        import socket, subprocess, sys
        from pathlib import Path

        # Check if port 8501 is already occupied
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        res = sock.connect_ex(('127.0.0.1', 8501))
        sock.close()
        if res == 0:
            logger.info("AI Gym Coach Engine is already active on port 8501.")
            return

        # Discover workspace root directory containing the Streamlit app
        backend_dir = Path(__file__).resolve().parent.parent
        workspace_dir = backend_dir.parent
        coach_script = workspace_dir / "ai-gym-coach-main" / "Main App" / "main.py"

        if not coach_script.exists():
            coach_script = workspace_dir / "ai-gym-coach-main - Copy" / "Main App" / "main.py"

        if not coach_script.exists():
            coach_script = backend_dir / "ai-gym-coach-main" / "Main App" / "main.py"

        if not coach_script.exists():
            coach_script = backend_dir / "ai-gym-coach-main - Copy" / "Main App" / "main.py"

        if coach_script.exists():
            logger.info("Activating AI Gym Coach Engine on port 8501 (%s)...", coach_script)
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(coach_script),
                    "--server.port",
                    "8501",
                    "--server.address",
                    "0.0.0.0",
                    "--server.headless",
                    "true",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(coach_script.parent.parent),
            )
            logger.info("AI Gym Coach Engine launched successfully in background!")
        else:
            logger.warning("AI Gym Coach script not found at %s", coach_script)
    except Exception as exc:
        logger.error("Could not auto-activate AI Gym Coach Engine: %s", exc)


# ─── Application Lifespan Hooks ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager handling startup initialization and teardown tasks.
    """
    logger.info("ATHLETIX backend starting up — environment: %s", settings.APP_ENV)
    start_streamlit_coach_background()
    yield
    logger.info("ATHLETIX backend shutting down.")


# ─── FastAPI Application Instance ─────────────────────────────────────────────
app = FastAPI(
    title="ATHLETIX API",
    description="AI-Powered Sports Talent Assessment Platform — REST API Backend",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── CORS Middleware Configuration ────────────────────────────────────────────
# Allows mobile app, Expo web development server, and authorized web clients to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Standardizes HTTPException payloads into a consistent API response schema.
    """
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches unhandled runtime exceptions and returns a clean, secure error format.
    Prevents sensitive server traces from leaking to client applications.
    """
    logger.exception("Unhandled server exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again.",
            },
        },
    )


# ─── Route Registration ───────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,          prefix=f"{API_PREFIX}/auth",          tags=["Auth"])
app.include_router(users.router,         prefix=f"{API_PREFIX}/users",         tags=["Users"])
app.include_router(videos.router,        prefix=f"{API_PREFIX}/videos",        tags=["Videos"])
app.include_router(assessments.router,   prefix=f"{API_PREFIX}/assessments",   tags=["Assessments"])
app.include_router(leaderboard.router,   prefix=f"{API_PREFIX}/leaderboard",   tags=["Leaderboard"])
app.include_router(verifications.router, prefix=f"{API_PREFIX}/verifications", tags=["Verifications"])
app.include_router(shortlists.router,    prefix=f"{API_PREFIX}/shortlists",    tags=["Shortlists"])
app.include_router(notifications.router, prefix=f"{API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(admin.router,         prefix=f"{API_PREFIX}/admin",         tags=["Admin"])
app.include_router(live_coach.router,    prefix=f"{API_PREFIX}/live",          tags=["Live Coach"])
app.include_router(push_tokens.router,   prefix=f"{API_PREFIX}/push-tokens",   tags=["Push Tokens"])


# ─── Health Check Endpoint ────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Liveness and health-check endpoint for container orchestration and uptime monitors.
    """
    return {"success": True, "data": {"status": "ok", "env": settings.APP_ENV}}
