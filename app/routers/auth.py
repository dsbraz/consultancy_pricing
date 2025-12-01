from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.microsoft import MicrosoftSSO
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID", "")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET", "")
MS_TENANT_ID = os.environ.get("MS_TENANT_ID", "")

# Base URL for redirect construction
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
REDIRECT_URI = f"{BASE_URL}/auth/callback"

# Initialize SSO only if credentials are present (to avoid startup errors if not configured yet)
if not MS_CLIENT_ID or not MS_CLIENT_SECRET or not MS_TENANT_ID:
    logger.error("CRITICAL: Microsoft SSO credentials not found in environment variables!")
    logger.error(f"MS_CLIENT_ID: {'SET' if MS_CLIENT_ID else 'MISSING'}")
    logger.error(f"MS_CLIENT_SECRET: {'SET' if MS_CLIENT_SECRET else 'MISSING'}")
    logger.error(f"MS_TENANT_ID: {'SET' if MS_TENANT_ID else 'MISSING'}")
    # We don't raise exception here to allow app to start, but auth will fail
else:
    logger.info("Microsoft SSO credentials loaded successfully.")

sso = MicrosoftSSO(
    client_id=MS_CLIENT_ID,
    client_secret=MS_CLIENT_SECRET,
    tenant=MS_TENANT_ID,
    redirect_uri=REDIRECT_URI,
    allow_insecure_http=True,  # Allow HTTP for local development
)


@router.get("/auth/login")
async def auth_login():
    """Redirects the user to the Microsoft login page."""
    return await sso.get_login_redirect()


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Processes the login callback from Microsoft."""
    try:
        user = await sso.verify_and_process(request)

        # Store essential user info in the session
        request.session["user"] = {
            "email": user.email,
            "display_name": user.display_name,
            "id": user.id,
            "picture": user.picture,
        }

        logger.info(f"User logged in: {user.email}")
        return RedirectResponse(url="/frontend/index.html")
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.get("/auth/logout")
async def auth_logout(request: Request):
    """Clears the user session and redirects to home."""
    request.session.clear()
    return RedirectResponse(url="/frontend/index.html")


@router.get("/auth/me")
async def auth_me(request: Request):
    """Returns the current authenticated user or 401."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
