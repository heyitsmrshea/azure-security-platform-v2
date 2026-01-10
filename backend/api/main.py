"""
Azure Security Platform V2 - FastAPI Application

Multi-tenant security dashboard backend with Azure AD authentication.
"""
import os
from contextlib import asynccontextmanager
from typing import Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # This loads .env from current directory

import structlog
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes import executive, it_staff, tenants, reports, auth, msp, compliance
from .dependencies import get_current_user, validate_token
from services.cache_service import CacheService
from services.cosmos_service import CosmosService
from services.scheduler import scheduler_service, historical_snapshot_scheduler
from services.live_data_service import get_live_data_service

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
    
    # CORS - supports comma-separated list in env var
    # Default includes common local development ports
    _default_origins = "http://localhost:3000,http://localhost:3001,http://localhost:8080"
    CORS_ORIGINS: list = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]
    
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
    
    # Start the scheduler service
    scheduler_service.start()
    logger.info("scheduler_service_started")
    
    # Set up daily snapshots if Graph API is configured
    try:
        live_service = get_live_data_service()
        if live_service.is_connected():
            # For production, you'd loop through configured tenants
            # For now, set up for the primary tenant
            tenant_id = settings.AZURE_AD_TENANT_ID
            if tenant_id:
                historical_snapshot_scheduler.setup_daily_snapshots(tenant_id, live_service)
                logger.info("historical_snapshots_configured", tenant_id=tenant_id)
    except Exception as e:
        logger.warning("scheduler_setup_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")
    
    # Shutdown scheduler
    scheduler_service.shutdown(wait=True)
    logger.info("scheduler_service_stopped")
    
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
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from services.live_data_service import get_live_data_service
    from services.storage_service import get_storage_service
    
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
    
    # Check Graph API connection
    try:
        live_service = get_live_data_service()
        health["services"]["graph_api"] = {
            "status": "connected" if live_service.is_connected() else "not_configured"
        }
    except Exception as e:
        health["services"]["graph_api"] = {"status": "error", "error": str(e)}
    
    # Check Storage Service
    try:
        storage = get_storage_service()
        storage_type = type(storage).__name__
        health["services"]["storage"] = {
            "status": "available",
            "type": storage_type,
        }
    except Exception as e:
        health["services"]["storage"] = {"status": "error", "error": str(e)}
    
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

app.include_router(
    msp.router,
    prefix="/api/msp",
    tags=["MSP Dashboard"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    compliance.router,
    prefix="/api/{tenant_id}/compliance",
    tags=["Compliance"],
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
