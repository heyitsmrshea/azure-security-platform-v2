"""
Azure Security Platform V2 - FastAPI Application

Multi-tenant security dashboard backend with Azure AD authentication.
"""
import os
from contextlib import asynccontextmanager
from typing import Optional

import structlog
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from .routes import executive, it_staff, tenants, reports, auth
from ..services.cache_service import CacheService
from ..services.cosmos_service import CosmosService

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Application settings from environment variables."""
    
    # Azure AD
    AZURE_AD_TENANT_ID: str = os.getenv("AZURE_AD_TENANT_ID", "")
    AZURE_AD_CLIENT_ID: str = os.getenv("AZURE_AD_CLIENT_ID", "")
    AZURE_AD_CLIENT_SECRET: str = os.getenv("AZURE_AD_CLIENT_SECRET", "")
    
    # Azure Resources
    KEY_VAULT_URL: str = os.getenv("KEY_VAULT_URL", "")
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # JWT Validation
    JWKS_URL: str = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
    ISSUER: str = f"https://sts.windows.net/{AZURE_AD_TENANT_ID}/"
    AUDIENCE: str = AZURE_AD_CLIENT_ID


settings = Settings()

# ============================================================================
# Service Instances
# ============================================================================

cache_service: Optional[CacheService] = None
cosmos_service: Optional[CosmosService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    global cache_service, cosmos_service
    
    logger.info("application_starting")
    
    # Initialize Redis cache
    if settings.REDIS_URL:
        cache_service = CacheService(redis_url=settings.REDIS_URL)
        await cache_service.connect()
        logger.info("redis_connected")
    
    # Initialize CosmosDB
    if settings.COSMOS_ENDPOINT and settings.COSMOS_KEY:
        cosmos_service = CosmosService(
            endpoint=settings.COSMOS_ENDPOINT,
            key=settings.COSMOS_KEY,
        )
        await cosmos_service.initialize()
        logger.info("cosmos_initialized")
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")
    
    if cache_service:
        await cache_service.disconnect()
    
    if cosmos_service:
        await cosmos_service.close()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Azure Security Platform V2",
    description="Multi-tenant security dashboard for post-ransomware visibility and IT accountability",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Azure AD Authentication
# ============================================================================

security = HTTPBearer()
_jwks_cache: Optional[dict] = None


async def get_jwks() -> dict:
    """Fetch and cache JWKS from Azure AD."""
    global _jwks_cache
    
    if _jwks_cache:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.JWKS_URL)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate Azure AD JWT token.
    
    Returns:
        Decoded token payload with user claims
    """
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
            audience=settings.AUDIENCE,
            issuer=settings.ISSUER,
        )
        
        return payload
        
    except JWTError as e:
        logger.warning("token_validation_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token: dict = Depends(validate_token)) -> dict:
    """Extract user info from validated token."""
    return {
        "user_id": token.get("oid"),
        "email": token.get("preferred_username") or token.get("upn"),
        "name": token.get("name"),
        "roles": token.get("roles", []),
    }


# ============================================================================
# Dependency Injection
# ============================================================================

def get_cache_service() -> CacheService:
    """Get cache service instance."""
    if not cache_service:
        raise HTTPException(status_code=503, detail="Cache service unavailable")
    return cache_service


def get_cosmos_service() -> CosmosService:
    """Get CosmosDB service instance."""
    if not cosmos_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    return cosmos_service


# ============================================================================
# Include Routers
# ============================================================================

# Public routes (no auth required for health check)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health = {
        "status": "healthy",
        "version": "2.0.0",
        "services": {},
    }
    
    # Check Redis
    if cache_service:
        health["services"]["redis"] = await cache_service.health_check()
    else:
        health["services"]["redis"] = {"status": "not_configured"}
    
    # Check CosmosDB
    if cosmos_service:
        health["services"]["cosmos"] = {"status": "connected"}
    else:
        health["services"]["cosmos"] = {"status": "not_configured"}
    
    return health


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Azure Security Platform V2",
        "version": "2.0.0",
        "docs": "/docs",
    }


# Include API routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
)

app.include_router(
    tenants.router,
    prefix="/api/tenants",
    tags=["Tenants"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    executive.router,
    prefix="/api/{tenant_id}/executive",
    tags=["Executive Dashboard"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    it_staff.router,
    prefix="/api/{tenant_id}/it-staff",
    tags=["IT Staff Dashboard"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    reports.router,
    prefix="/api/{tenant_id}/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user)],
)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc) if os.getenv("DEBUG") else None,
    }
