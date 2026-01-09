# Azure Security Platform V2 - Requirements Document

**Created:** January 9, 2026  
**Purpose:** Multi-tenant security dashboard for post-ransomware visibility and IT accountability

---

## Executive Summary

Build a web-based security dashboard with two distinct views:
- **Executive Dashboard**: High-level metrics for CEO/Board - simple, clear, accountable
- **IT Staff Dashboard**: Technical details for operations team

**Key Drivers:**
- Recent ransomware attack created need for visibility
- CEO needs to verify IT staff work (trust but verify)
- Board/investor reporting on security posture
- Show compliance and improvement over time

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────┤
│ Microsoft Graph API    │ Azure Resource Manager │ Defender APIs │
│ - Secure Score         │ - Backup Vaults        │ - Alerts      │
│ - Identity Protection  │ - Backup Jobs          │ - Incidents   │
│ - Conditional Access   │ - Protected Items      │ - Vulns       │
│ - PIM/Roles            │                        │               │
│ - Intune Devices       │                        │               │
│ - Audit Logs           │                        │               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│ Data Collectors │ Tenant Manager │ REST API │ Report Generator  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ CosmosDB │   │  Redis   │   │ Frontend │
        │ (data)   │   │ (cache)  │   │ (Next.js)│
        └──────────┘   └──────────┘   └──────────┘
```

---

## Multi-Tenant Support

- **Model**: MSP-style, serving multiple client tenants
- **Data Isolation**: CosmosDB partitioned by tenantId
- **UI**: Tenant selector in navigation
- **Auth**: Azure AD with per-tenant credentials stored securely

---

## Executive Dashboard Sections

### Row 1: Primary Metrics
1. **Security Score** - Microsoft Secure Score (0-100) with trend arrow and industry comparison ("Top 35%")
2. **Compliance Score** - Framework compliance % with trend
3. **Risk Count** - Critical/High findings with change indicator

### Row 2: Ransomware Readiness (POST-ATTACK PRIORITY)
4. **Backup Health** - % of critical systems backed up successfully
5. **Last Successful Backup** - Time since last backup completed
6. **Recovery Readiness** - RTO/RPO status indicator (Green/Yellow/Red)

### Row 3: Identity & Access
7. **MFA Coverage** - % with MFA (Admins vs. All Users breakdown)
8. **Privileged Accounts** - Global Admin count with trend
9. **Risky Users** - Count requiring investigation

### Row 4: Threat Summary
10. **Active Alerts** - By severity (Critical/High/Medium)
11. **Blocked Threats** - Phishing, malware blocked this month
12. **Device Compliance** - % compliant devices

### Row 5: IT Accountability Metrics
13. **Patch SLA Compliance** - % meeting patch timeline (with target)
14. **Open Finding Age** - Distribution chart (0-7, 7-30, 30-90, 90+)
15. **MTTR** - Mean time to remediate in days

### Row 6: Progress & Trends
16. **6-Month Score Trend** - Line chart showing improvement
17. **Top 5 Risks** - Plain English descriptions
18. **Data Freshness Indicator** - "Last updated: X minutes ago"

---

## IT Staff Dashboard Sections

### Alerts & Incidents
1. Alert Queue - Sortable/filterable list with severity, age, resource
2. Incident Timeline - Recent incidents with status

### Vulnerability Management
3. Vulnerability Summary - Cards by severity and age
4. Top Vulnerable Assets - Systems needing immediate attention
5. CVE Details Table - Searchable with filters

### Identity & Access
6. MFA Gaps - Users without MFA by department
7. Conditional Access Coverage - Policies and gaps
8. Privileged Access Inventory - All admin accounts, last activity
9. Risky Sign-ins - Recent suspicious activity log

### Device Security
10. Non-Compliant Devices - With compliance failure reasons
11. Agent Health - EDR/Antivirus status
12. Unmanaged Devices - Accessing corporate data

### Third-Party/Vendor Risk
13. Guest User Inventory - External users with access levels
14. App Permissions - Third-party apps with admin consent
15. External Sharing Stats - Files/folders shared externally

### Backup & Recovery
16. Backup Job Status - Success/failure per protected item
17. Unprotected Assets - Critical systems without backup
18. Last Recovery Test - Date per system

### Audit Trail
19. Recent Admin Actions - Policy changes, role assignments
20. High-Risk Operations - Sensitive actions audit log

---

## Data Collection Endpoints

### Microsoft Graph API
| Metric | Endpoint | Frequency |
|--------|----------|-----------|
| Secure Score | `/security/secureScores` | 4 hours |
| MFA Status | `/reports/authenticationMethods/userRegistrationDetails` | 4 hours |
| Risky Users | `/identityProtection/riskyUsers` | 1 hour |
| Security Alerts | `/security/alerts_v2` | 15 min |
| Conditional Access | `/identity/conditionalAccess/policies` | 1 hour |
| PIM Assignments | `/roleManagement/directory/roleAssignments` | 1 hour |
| Audit Logs | `/auditLogs/directoryAudits` | 30 min |
| Device Compliance | Intune: `/deviceManagement/managedDevices` | 4 hours |
| Guest Users | `/users?$filter=userType eq 'Guest'` | Daily |

### Azure Resource Manager
| Metric | Endpoint | Frequency |
|--------|----------|-----------|
| Backup Vaults | Recovery Services Vaults API | 4 hours |
| Backup Jobs | Backup Jobs API | 4 hours |
| Protected Items | Backup Protected Items API | 4 hours |

### Calculated Metrics (from CosmosDB history)
| Metric | Calculation |
|--------|-------------|
| Patch SLA Compliance | % of vulns patched within policy window |
| MTTR | Avg days from finding creation to resolution |
| Finding Age Distribution | Count by bucket (0-7, 7-30, 30-90, 90+) |

---

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

---

## UI/Design System

### Design Philosophy
Enterprise Security Aesthetic - Clean, authoritative, data-dense. No unnecessary decoration.

### Color Palette (Dark Theme Only)
```
Background:
  Primary:    #0F172A (Slate 900 - deep navy)
  Secondary:  #1E293B (Slate 800 - cards)
  Tertiary:   #334155 (Slate 700 - borders)

Text:
  Primary:    #F8FAFC (Slate 50 - headings)
  Secondary:  #94A3B8 (Slate 400 - labels)
  Muted:      #64748B (Slate 500 - timestamps)

Severity:
  Critical:   #EF4444 (Red 500)
  High:       #F97316 (Orange 500)
  Medium:     #EAB308 (Yellow 500)
  Low:        #3B82F6 (Blue 500)
  Success:    #22C55E (Green 500)
```

### Typography
- Font: Inter
- Large KPIs: 48px Bold
- Section Headers: 20px Semibold
- Labels: 12px Medium Uppercase
- Body: 14px Regular

### Component Patterns
- Metric Cards: Large number + trend + comparison
- Data Tables: Alternating rows, sortable, expandable
- Charts: Minimal, no gridlines, subtle gradients

### No-Go List
- No gradients on backgrounds
- No emoji in UI
- No excessive animations
- No light mode
- No stock photos

---

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- Azure Identity SDK
- Microsoft Graph SDK
- Azure Management SDKs
- APScheduler
- Redis (caching)
- CosmosDB (persistence)
- ReportLab/WeasyPrint (PDF)

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Recharts
- MSAL React
- TanStack Query

### Infrastructure
- Azure App Service
- Azure CosmosDB
- Azure Cache for Redis
- Azure Key Vault
- Azure AD App Registration

---

## Project Structure

```
azure_security_platform_v2/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── executive.py
│   │   │   ├── it_staff.py
│   │   │   ├── tenants.py
│   │   │   ├── reports.py
│   │   │   └── auth.py
│   │   └── main.py
│   ├── collectors/
│   │   ├── secure_score.py
│   │   ├── identity.py
│   │   ├── devices.py
│   │   ├── threats.py
│   │   ├── backup.py
│   │   ├── vendor_risk.py
│   │   └── accountability.py
│   ├── services/
│   │   ├── graph_client.py
│   │   ├── azure_client.py
│   │   ├── tenant_manager.py
│   │   └── cache_service.py
│   ├── models/
│   │   └── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── [tenantId]/
│   │   │   │   ├── executive/
│   │   │   │   └── it-staff/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── executive/
│   │   │   ├── it-staff/
│   │   │   └── shared/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── tailwind.config.js
└── infrastructure/
    ├── bicep/
    └── terraform/
```

---

## Implementation Phases

### Phase 1: Backend Foundation (Week 1)
- FastAPI project setup with Azure AD auth
- Multi-tenant manager with data isolation
- Graph API client
- Azure RM client for backup APIs
- CosmosDB integration

### Phase 2: Data Collectors (Week 1-2)
- Secure Score + benchmark
- Identity (MFA, risky users, PIM)
- Threats (alerts, incidents)
- Device compliance
- Azure Backup health
- Accountability metrics calculator

### Phase 3: Executive Dashboard (Week 2)
- Next.js setup with MSAL
- Tenant selector
- All metric cards
- Backup health / ransomware readiness
- IT accountability section
- Trend charts

### Phase 4: IT Staff Dashboard (Week 3)
- Alert queue with filtering
- Vulnerability view
- Device compliance
- Privileged access inventory
- Third-party risk section
- Backup job status

### Phase 5: Polish (Week 4)
- PDF report generator
- Export functionality
- Historical charts
- Responsive design
- Redis caching
- Scheduled jobs

---

## Key Decisions Made

1. **Multi-tenant**: Yes (MSP model)
2. **Backup Solution**: Azure Backup only (can integrate via API)
3. **Task Tracking**: Metrics only (no built-in ticketing)
4. **Notifications**: Not needed (user will check dashboard)
5. **Theme**: Dark mode only

---

## Files to Create First

1. backend/requirements.txt
2. backend/api/main.py
3. backend/services/graph_client.py
4. backend/collectors/secure_score.py
5. frontend/package.json
6. frontend/tailwind.config.js
7. frontend/src/app/layout.tsx
8. frontend/src/components/executive/SecurityScoreCard.tsx

