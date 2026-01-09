"""
Authentication routes for Azure Security Platform V2
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..main import validate_token, get_current_user

router = APIRouter()


class UserInfo(BaseModel):
    user_id: str
    email: str
    name: str
    roles: list[str]


@router.get("/me", response_model=UserInfo)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserInfo(
        user_id=user.get("user_id", ""),
        email=user.get("email", ""),
        name=user.get("name", ""),
        roles=user.get("roles", []),
    )


@router.post("/validate")
async def validate_auth(token: dict = Depends(validate_token)):
    """Validate authentication token."""
    return {
        "valid": True,
        "expires": token.get("exp"),
        "scopes": token.get("scp", "").split(" "),
    }
