from fastapi import HTTPException, Request, status

async def get_current_user(request: Request):
    """
    Dependency to verify that the user is authenticated.
    Raises 401 if no user is found in the session.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

