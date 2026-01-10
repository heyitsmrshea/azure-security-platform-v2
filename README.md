# Azure Security Platform V2

Multi-tenant security dashboard for post-ransomware visibility and IT accountability.

## Overview

This platform provides two dashboard views:
- **Executive Dashboard**: High-level metrics for CEO/Board - simple, clear, accountable
- **IT Staff Dashboard**: Technical details for operations team

### Key Features

- **Real-Time Data**: Live integration with Microsoft Graph API and Azure Resource Manager for up-to-the-minute security insights.
- **Post-Ransomware Focus**: Specialized metrics for backup health, recovery readiness (RTO/RPO), and threat summary.
- **IT Accountability Metrics**: Track patch SLA compliance, finding age distribution, and MTTR.
- **Multi-Tenant**: Designed for MSPs with robust tenant isolation using CosmosDB partitions.

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- Azure Identity SDK
- Microsoft Graph SDK
- CosmosDB
- Redis (caching)

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Recharts
- MSAL React

## Project Structure

```
azure_security_platform_v2/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── executive.py      # Executive dashboard endpoints
│   │   │   ├── it_staff.py       # IT staff dashboard endpoints
│   │   │   ├── tenants.py        # Tenant management
│   │   │   ├── reports.py        # Report generation
│   │   │   └── auth.py           # Authentication
│   │   └── main.py               # FastAPI app
│   ├── collectors/
│   │   ├── secure_score.py       # Microsoft Secure Score
│   │   ├── identity.py           # MFA, PIM, risky users
│   │   └── backup.py             # Azure Backup health
│   ├── services/
│   │   ├── graph_client.py       # Microsoft Graph API
│   │   ├── azure_client.py       # Azure Resource Manager
│   │   ├── tenant_manager.py     # Multi-tenant management
│   │   ├── cache_service.py      # Redis caching
│   │   └── cosmos_service.py     # CosmosDB persistence
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── [tenantId]/executive/  # Executive dashboard
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── executive/        # Executive-specific components
│   │   │   ├── it-staff/         # IT staff components
│   │   │   └── shared/           # Shared components
│   │   ├── lib/
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── dashboard.ts
│   ├── package.json
│   └── tailwind.config.js
└── infrastructure/
    ├── bicep/
    └── terraform/
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Azure AD and database credentials:
# - AZURE_AD_TENANT_ID
# - AZURE_AD_CLIENT_ID
# - AZURE_AD_CLIENT_SECRET
# - REDIS_URL
# - COSMOS_ENDPOINT
# - COSMOS_KEY

# Run the server
uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## API Permissions Required

### Microsoft Graph API
- SecurityEvents.Read.All
- IdentityRiskyUser.Read.All
- Policy.Read.All
- RoleManagement.Read.Directory
- DeviceManagementManagedDevices.Read.All
- Reports.Read.All
- User.Read.All
- AuditLog.Read.All
- Directory.Read.All

### Azure Resource Manager
- Microsoft.RecoveryServices/vaults/read
- Microsoft.RecoveryServices/vaults/backupJobs/read
- Microsoft.RecoveryServices/vaults/backupProtectedItems/read

## Design System

Dark theme only with enterprise security aesthetic.

### Colors
- Background Primary: #0F172A (Slate 900)
- Background Secondary: #1E293B (Slate 800)
- Text Primary: #F8FAFC (Slate 50)
- Severity Critical: #EF4444 (Red 500)
- Severity High: #F97316 (Orange 500)
- Status Success: #22C55E (Green 500)

### Typography
- Font: Inter
- Large KPIs: 48px Bold
- Section Headers: 20px Semibold
- Labels: 12px Medium Uppercase

## Dashboard Sections

### Executive Dashboard
1. Security Score (with trend and industry comparison)
2. Compliance Score
3. Risk Count (Critical/High)
4. Backup Health (% protected)
5. Last Successful Backup
6. Recovery Readiness (RTO/RPO)
7. MFA Coverage (Admins vs All)
8. Privileged Accounts (Global Admin count)
9. Risky Users
10. Active Alerts
11. Blocked Threats
12. Device Compliance
13. Patch SLA Compliance
14. Open Finding Age Distribution
15. MTTR (Mean Time to Remediate)
16. 6-Month Score Trend
17. Top 5 Risks (plain English)
18. Data Freshness Indicator

### IT Staff Dashboard
- Alert Queue (sortable/filterable)
- Vulnerability Summary
- MFA Gaps by Department
- Conditional Access Coverage
- Privileged Access Inventory
- Non-Compliant Devices
- Guest User Inventory
- Third-Party App Permissions
- Backup Job Status
- Audit Trail

## License

Proprietary - All rights reserved
