from fastapi import Header, HTTPException
from supabase_client import supabase


def get_current_user(
    authorization: str | None = Header(default=None),
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    token = authorization[7:]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user = response.user

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return user