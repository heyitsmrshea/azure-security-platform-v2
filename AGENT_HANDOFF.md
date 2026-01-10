# Agent Handoff Document
## Azure Security Platform V2

**Last Updated:** January 10, 2026
**Status:** Live Data Architecture Implemented

---

## 1. Project Overview

**Platform Purpose:** Multi-tenant security dashboard for MSPs to assess and monitor Azure environments using real-time data from Microsoft Graph API and Azure Resource Manager.

**Core Tech Stack:**
- **Backend:** FastAPI (Python 3.11+), Azure Identity, Microsoft Graph SDK, CosmosDB, Redis.
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui.
- **Infrastructure:** Docker, Azure App Service (targeted).

**Current State:**
- The core architecture is **fully implemented**.
- Real-time data fetching via Microsoft Graph is **wired and verified** for key metrics (MFA, Risky Users, Alerts).
- Executive and IT Staff dashboards are **functional** and rendering live data.
- Codebase is clean and ready for migration/deployment.

---

## 2. Feature Implementation Status

| Feature / Component | Status | Notes |
| :--- | :--- | :--- |
| **Backend Infrastructure** | ✅ **Complete** | FastAPI app, CORS, Middleware, Logging, Exception Handling. |
| **Authentication** | ✅ **Complete** | Azure AD integration, Token Validation, User Context dependency. |
| **Graph API Client** | ✅ **Complete** | `GraphClient` implements methods for Secure Score, Identity Protection, Intune, etc. |
| **Live Data Service** | ✅ **Complete** | Orchestrates data fetching, handles caching, falls back to mock data if needed. |
| **Executive Dashboard** | ✅ **Complete** | Full UI + API routes. Renders Secure Score, Risk metrics, Backup health. |
| **IT Staff Dashboard** | ✅ **Complete** | Full UI + API routes. Renders Alerts, Vulnerabilities, Audit logs. |
| **Tenant Management** | ✅ **Complete** | API routes for switching tenants, specific MSP dashboard routes. |
| **Compliance Module** | ⚠️ **Partial** | Routes exist (`compliance.py`), UI exists, but needs deeper mapping logic vs. simple scores. |
| **PDF Reporting** | ⚠️ **Partial** | `backend/reports/` has generators, but frontend integration for "Download PDF" needs verifying. |
| **Data Persistence** | ⚠️ **Partial** | CosmosDB service exists (`cosmos_service.py`), but historical trending logic needs to be enabled/verified. |
| **CI/CD** | ❌ **Todo** | Deployment pipelines (GitHub Actions/Azure DevOps) not yet defined. |

---

## 3. Immediate Next Steps

1.  **Verify Compliance & Reporting:** Deep dive into `backend/api/routes/compliance.py` and `backend/reports/` to ensure they produce accurate outputs similar to the Executive dashboard.
2.  **Enable Historical Trending:** Connect the `CosmosService` to the `LiveDataService` to start saving daily snapshots of scores for trend analysis.
3.  **Deployment Configuration:** Create `Dockerfile` for production (multi-stage builds) and set up `fly.toml` or `azure-pipelines.yml`.
4.  **Error Handling Polish:** Ensure graceful UI degradation if specific Graph API permissions are missing (e.g., Intune/Device data).

---

## 4. Complete File Manifest

### Configuration & Root
- `.env` (Local secrets - DO NOT COMMIT)
- `.env.example` (Template for secrets)
- `.gitignore`
- `README.md` (Project documentation)
- `ARCHITECTURE_MAP.md` (Component mapping)
- `AGENT_HANDOFF.md` (This file)
- `docker-compose.yml` (Local dev stack)
- `run_assessment.py` (CLI entry point)
- `REQUIREMENTS.md`

### Backend (`/backend`)
**API Layer (`backend/api/`)**
- `backend/api/main.py` (App entry point)
- `backend/api/dependencies.py` (Auth & Common deps)
- `backend/api/routes/auth.py`
- `backend/api/routes/executive.py`
- `backend/api/routes/it_staff.py`
- `backend/api/routes/tenants.py`
- `backend/api/routes/compliance.py`
- `backend/api/routes/reports.py`
- `backend/api/routes/msp.py`

**Business Logic (`backend/services/`)**
- `backend/services/live_data_service.py` (Core orchestrator)
- `backend/services/graph_client.py` (MS Graph integration)
- `backend/services/cosmos_service.py` (Database)
- `backend/services/cache_service.py` (Redis)
- `backend/services/tenant_manager.py`
- `backend/services/azure_client.py` (ARM integration)
- `backend/services/scheduler.py` (Background jobs)

**Data Models (`backend/models/`)**
- `backend/models/schemas.py` (Pydantic models)

**Collectors (`backend/collectors/`)**
- `backend/collectors/secure_score.py`
- `backend/collectors/identity.py`
- `backend/collectors/backup.py`
- `backend/collectors/devices.py`
- `backend/collectors/threats.py`
- `backend/collectors/accountability.py`
- `backend/collectors/vendor_risk.py`

**Reporting & Assessment (`backend/reports/`, `backend/assessment/`)**
- `backend/reports/pdf_generator.py`
- `backend/reports/evidence_generator.py`
- `backend/assessment/engine.py`
- `backend/assessment/grading.py`
- `backend/assessment/comparison.py`

**Config**
- `backend/requirements.txt`
- `backend/Dockerfile`

### Frontend (`/frontend`)
**App Router Pages (`frontend/src/app/`)**
- `frontend/src/app/page.tsx` (Landing)
- `frontend/src/app/layout.tsx` (Root Layout)
- `frontend/src/app/[tenantId]/executive/page.tsx`
- `frontend/src/app/[tenantId]/it-staff/page.tsx`
- `frontend/src/app/[tenantId]/compliance/page.tsx`
- `frontend/src/app/msp/overview/page.tsx`
- `frontend/src/app/demo/...` (Demo routes)

**Components (`frontend/src/components/`)**
- **Executive:** `RiskCard.tsx`, `TrendChart.tsx`, `HealthGrade.tsx`
- **IT Staff:** `AlertQueue.tsx`, `DataTable.tsx`, `AuditTrail.tsx`, `VulnerabilityView.tsx`
- **Shared:** `DashboardHeader.tsx`, `TenantSwitcher.tsx`, `MetricCard.tsx`, `StatusBadge.tsx`
- **Providers:** `Providers.tsx`

**Lib & Utils (`frontend/src/lib/`)**
- `frontend/src/lib/api-client.ts` (Frontend API wrapper)
- `frontend/src/lib/utils.ts` (Tailwind helpers)
- `frontend/src/lib/msal-config.ts` (Auth config)

**Config**
- `frontend/package.json`
- `frontend/tailwind.config.js`
- `frontend/next.config.js`
