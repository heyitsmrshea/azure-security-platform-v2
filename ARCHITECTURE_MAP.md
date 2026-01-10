# Architecture Map

This document maps high-level architectural components to their specific file paths in the codebase. It is intended to help AI agents and developers quickly locate core logic.

## 1. Backend Infrastructure (FastAPI)
- **Entry Point**: `backend/api/main.py` (FastAPI app definition, middleware, exception handlers)
- **Configuration**: `backend/api/main.py` ("Settings" class), `backend/.env` (runtime config)
- **Environment Template**: `backend/.env.example`

## 2. API Layer
- **Route Definitions**: `backend/api/routes/`
    - **Executive Dashboard**: `backend/api/routes/executive.py`
    - **IT Staff Dashboard**: `backend/api/routes/it_staff.py`
    - **Tenant Management**: `backend/api/routes/tenants.py`
    - **Compliance**: `backend/api/routes/compliance.py`
    - **Reports**: `backend/api/routes/reports.py`
    - **Auth**: `backend/api/routes/auth.py`
- **Dependencies**: `backend/api/dependencies.py` (Auth token validation, user context)

## 3. Service Layer (Business Logic)
- **Location**: `backend/services/`
- **Microsoft Graph Integration**: `backend/services/graph_client.py` (Real-time data fetching)
- **Live Data Orchestration**: `backend/services/live_data_service.py`
- **Database Access**: `backend/services/cosmos_service.py`
- **Caching**: `backend/services/cache_service.py`
- **Tenant Management**: `backend/services/tenant_manager.py`

## 4. Frontend Application (Next.js 14)
- **Entry Point**: `frontend/src/app/layout.tsx` (Root layout, providers)
- **Configuration**: `frontend/next.config.js`, `frontend/tailwind.config.js`
- **Package Manifest**: `frontend/package.json`

## 5. Frontend Pages (App Router)
- **Executive Dashboard**: `frontend/src/app/[tenantId]/executive/page.tsx`
- **IT Staff Dashboard**: `frontend/src/app/[tenantId]/it-staff/page.tsx` (or similar, check directory)
- **Dynamic Tenant Routing**: `frontend/src/app/[tenantId]/`

## 6. Frontend Components
- **Location**: `frontend/src/components/`
- **Executive Views**: `frontend/src/components/executive/`
- **IT Staff Views**: `frontend/src/components/it-staff/`
- **Shared UI**: `frontend/src/components/shared/` & `frontend/src/components/ui/` (shadcn/ui)

## 7. Data Models
- **Backend Schema**: `backend/models/schemas.py` (Pydantic models)
- **Frontend Types**: `frontend/src/types/`
