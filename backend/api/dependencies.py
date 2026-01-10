"""
FastAPI dependencies for authentication and services.

Separated from main.py to avoid circular imports.
"""
import os
from typing import Optional

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# Settings
AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID", "")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID", "")
JWKS_URL = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://sts.windows.net/{AZURE_AD_TENANT_ID}/"
AUDIENCE = AZURE_AD_CLIENT_ID

security = HTTPBearer(auto_error=False)
_jwks_cache: Optional[dict] = None


async def get_jwks() -> dict:
    """Fetch and cache JWKS from Azure AD."""
    global _jwks_cache
    
    if _jwks_cache:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


async def validate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Validate Azure AD JWT token.
    
    Returns:
        Decoded token payload with user claims
    """
    # Allow unauthenticated access in demo mode
    if not credentials:
        return {"demo": True, "oid": "demo-user", "name": "Demo User"}
    
    token = credentials.credentials
    
    try:
        # Get JWKS
        jwks = await get_jwks()
        
        # Get token header to find key ID
        unverified_header = jwt.get_unverified_header(token)
        
        # Find matching key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find key")
        
        # Validate token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token: dict = Depends(validate_token)) -> dict:
    """Extract user info from validated token."""
    if token.get("demo"):
        return {
            "user_id": "demo-user",
            "email": "demo@example.com",
            "name": "Demo User",
            "roles": ["admin"],
        }
    
    return {
        "user_id": token.get("oid"),
        "email": token.get("preferred_username") or token.get("upn"),
        "name": token.get("name"),
        "roles": token.get("roles", []),
    }
