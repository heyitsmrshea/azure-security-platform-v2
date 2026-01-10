# Azure Security Platform - Snapshot Assessment Architecture

**Last Updated:** January 9, 2026  
**Purpose:** Point-in-time security assessments for customer engagements

---

## Business Model

### Service Delivery
- **You run the scans** (maintains IP, ensures quality)
- **Customers grant access** via OAuth consent (multi-tenant app)
- **Deliverables**: PDF reports (executive + technical) with optional white-labeling

### Pricing Tiers (Suggested)
| Tier | Includes | Use Case |
|------|----------|----------|
| **Basic** | Executive Summary + Top 10 Findings | Quick health check |
| **Standard** | Full report + All frameworks | Quarterly assessment |
| **Premium** | Standard + Comparison + Remediation tracking | Ongoing engagement |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SNAPSHOT ASSESSMENT WORKFLOW                          │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
  │  ONBOARD   │───▶│  COLLECT   │───▶│  ANALYZE   │───▶│  DELIVER   │
  │  Customer  │    │    Data    │    │  + Score   │    │   Report   │
  └────────────┘    └────────────┘    └────────────┘    └────────────┘
        │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼
   OAuth Consent     Graph API +       Framework         PDF/Word
   Multi-tenant      Azure ARM         Mapping           White-labeled
   App Registration  ~2-5 minutes      CIS/NIST/SOC2     Executive + Tech

```

---

## Customer Onboarding (OAuth Consent)

### Why OAuth Consent?
- **Customer-friendly**: One-click authorization, no manual SP creation
- **Secure**: Time-limited tokens, auditable access
- **Scalable**: Same app registration for all customers
- **Revocable**: Customer can revoke access anytime

### Your App Registration (Multi-Tenant)
```
Azure AD App Registration:
├── Application (client) ID: <your-app-id>
├── Supported account types: "Accounts in any organizational directory"
├── Redirect URIs: 
│   └── https://your-domain.com/auth/callback (or localhost for CLI)
└── API Permissions (Application, not Delegated):
    ├── Microsoft Graph
    │   ├── SecurityEvents.Read.All
    │   ├── IdentityRiskyUser.Read.All
    │   ├── Policy.Read.All
    │   ├── RoleManagement.Read.Directory
    │   ├── DeviceManagementManagedDevices.Read.All
    │   ├── Reports.Read.All
    │   ├── User.Read.All
    │   ├── AuditLog.Read.All
    │   └── Directory.Read.All
    └── Azure Service Management
        └── user_impersonation
```

### Consent Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                      CUSTOMER CONSENT FLOW                       │
└─────────────────────────────────────────────────────────────────┘

1. You send customer a consent URL:
   https://login.microsoftonline.com/{customer-tenant}/adminconsent
   ?client_id={your-app-id}
   &redirect_uri={your-callback}
   &scope=https://graph.microsoft.com/.default

2. Customer's Global Admin clicks the link

3. Microsoft shows permission dialog:
   "OperationMOS Security Assessment wants to:
    ✓ Read security information
    ✓ Read identity protection data
    ✓ Read user profiles
    ..."

4. Admin clicks "Accept"

5. Your app can now access their tenant using:
   - Tenant ID (from consent callback)
   - Your client credentials (client_id + client_secret)
```

---

## CLI Assessment Tool

### Usage
```bash
# Run assessment for a customer
python run_assessment.py \
  --tenant-id "customer-tenant-id" \
  --customer-name "Acme Corporation" \
  --output-dir "./assessments/acme-2026-01-09" \
  --frameworks cis,nist,soc2,iso27001 \
  --brand "operationmos"  # or custom brand config

# Compare with previous assessment
python run_assessment.py \
  --tenant-id "customer-tenant-id" \
  --customer-name "Acme Corporation" \
  --compare-with "./assessments/acme-2025-10-15" \
  --output-dir "./assessments/acme-2026-01-09"
```

### Output Structure
```
assessments/
└── acme-2026-01-09/
    ├── manifest.json              # Assessment metadata
    ├── raw_data/                  # Collected data (encrypted, delete after)
    │   ├── secure_score.json
    │   ├── identity.json
    │   ├── devices.json
    │   ├── backup.json
    │   └── threats.json
    ├── analysis/
    │   ├── findings.json          # All findings with severity
    │   ├── compliance/
    │   │   ├── cis_azure_v2.json
    │   │   ├── nist_800_53.json
    │   │   ├── soc2.json
    │   │   └── iso27001.json
    │   └── scores.json            # Calculated scores
    ├── reports/
    │   ├── executive_summary.pdf
    │   ├── technical_findings.pdf
    │   ├── compliance_report.pdf
    │   └── comparison_report.pdf  # If comparing
    └── evidence/                   # For auditors
        ├── screenshots/
        └── api_responses/
```

---

## Assessment Manifest

```json
{
  "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "2.0.0",
  "customer": {
    "name": "Acme Corporation",
    "tenant_id": "12345678-1234-1234-1234-123456789abc",
    "primary_domain": "acme.onmicrosoft.com"
  },
  "assessment": {
    "date": "2026-01-09T14:30:00Z",
    "duration_seconds": 245,
    "assessor": "OperationMOS",
    "type": "point_in_time",
    "frameworks": ["CIS Azure 2.0", "NIST 800-53", "SOC 2", "ISO 27001"]
  },
  "scores": {
    "overall_grade": "B",
    "overall_score": 72,
    "secure_score": 72.5,
    "compliance": {
      "cis_azure_v2": 68,
      "nist_800_53": 71,
      "soc2": 75,
      "iso27001": 69
    },
    "categories": {
      "identity": 85,
      "data_protection": 68,
      "network": 71,
      "devices": 78,
      "backup": 94
    }
  },
  "findings": {
    "critical": 3,
    "high": 12,
    "medium": 45,
    "low": 89,
    "informational": 23
  },
  "comparison": {
    "previous_assessment": "2025-10-15",
    "score_change": "+5",
    "findings_resolved": 18,
    "new_findings": 7
  },
  "branding": {
    "company": "OperationMOS",
    "logo": "assets/logos/operationmos_full.svg",
    "colors": {
      "primary": "#0F172A",
      "accent": "#3B82F6"
    }
  }
}
```

---

## Grading System

### Overall Grade (A-F)
| Grade | Score Range | Description |
|-------|-------------|-------------|
| **A** | 90-100 | Excellent - Industry leading |
| **B** | 75-89 | Good - Above average |
| **C** | 60-74 | Fair - Meets minimum standards |
| **D** | 40-59 | Poor - Significant gaps |
| **F** | 0-39 | Critical - Immediate action required |

### Score Calculation
```python
overall_score = (
    secure_score * 0.30 +           # Microsoft's score
    identity_score * 0.25 +         # MFA, PIM, risky users
    data_protection_score * 0.15 +  # Encryption, DLP
    backup_score * 0.15 +           # Ransomware readiness
    device_score * 0.10 +           # Compliance, patching
    network_score * 0.05            # Firewall, NSGs
)
```

---

## Comparison Reports

### What We Compare
- **Score Changes**: Overall, category, and compliance scores
- **Findings**: New, resolved, unchanged
- **Trends**: Improvement areas vs. regression
- **Recommendations**: What was implemented vs. still open

### Visual Comparison
```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY SCORE COMPARISON                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  October 2025          January 2026         Change          │
│  ┌──────────┐          ┌──────────┐                         │
│  │    67    │   ──▶    │    72    │        +5 ↑            │
│  │    C     │          │    C     │                         │
│  └──────────┘          └──────────┘                         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  FINDINGS RESOLVED: 18                                       │
│  NEW FINDINGS: 7                                             │
│  NET IMPROVEMENT: -11 findings                               │
└─────────────────────────────────────────────────────────────┘
```

---

## White-Label Support

### Brand Configuration
```json
{
  "brand_id": "partner_xyz",
  "company_name": "Partner Security Services",
  "logo_path": "brands/partner_xyz/logo.svg",
  "colors": {
    "primary": "#1a365d",
    "secondary": "#2d3748",
    "accent": "#4299e1"
  },
  "contact": {
    "email": "security@partner.com",
    "phone": "+1-555-123-4567",
    "website": "https://partner.com"
  },
  "footer_text": "© 2026 Partner Security Services. Confidential.",
  "disclaimers": [
    "This assessment represents a point-in-time snapshot.",
    "Recommendations should be validated before implementation."
  ]
}
```

### Report Customization
- Logo placement on cover and headers
- Custom color scheme throughout
- Partner contact information
- Custom disclaimers and legal text
- Optional: Partner-specific recommendations

---

## Data Handling & Security

### Collection
- All API calls use TLS 1.3
- Credentials stored in environment variables (never in code)
- Customer tenant ID logged for audit trail

### Storage
- Raw data encrypted at rest (AES-256)
- Stored only for assessment duration
- Auto-delete raw data after report generation (configurable)

### Retention
- Assessment manifests: Keep indefinitely (for comparisons)
- Reports: Customer's choice
- Raw data: Delete after 7 days (or immediately)

### Customer Data Rights
- Customer can request data deletion
- No data shared with third parties
- Audit log of all access available

---

## Implementation Checklist

### Phase 1: Core Assessment Engine
- [ ] CLI runner (`run_assessment.py`)
- [ ] Assessment orchestrator
- [ ] All collectors wired up (no mock data)
- [ ] Manifest generation
- [ ] Basic PDF report

### Phase 2: Compliance Mapping
- [ ] CIS Azure v2 control mapping
- [ ] NIST 800-53 mapping
- [ ] SOC 2 criteria mapping
- [ ] ISO 27001 Annex A mapping

### Phase 3: Comparison Reports
- [ ] Previous assessment loading
- [ ] Diff calculation
- [ ] Comparison PDF section
- [ ] Trend visualization

### Phase 4: White-Labeling
- [ ] Brand configuration loader
- [ ] Logo placement in PDFs
- [ ] Color scheme application
- [ ] Custom footer/disclaimer

### Phase 5: Customer Portal (Future)
- [ ] OAuth consent landing page
- [ ] Assessment history view
- [ ] Report download
- [ ] Remediation tracking

---

## File Structure

```
azure_security_platform_v2/
├── run_assessment.py              # CLI entry point
├── backend/
│   ├── assessment/                # NEW: Assessment engine
│   │   ├── __init__.py
│   │   ├── engine.py              # Main orchestrator
│   │   ├── consent.py             # OAuth consent helpers
│   │   ├── grading.py             # Score calculation
│   │   └── comparison.py          # Diff engine
│   ├── collectors/                # Existing, wire up
│   ├── compliance/                # NEW: Framework mapping
│   │   ├── __init__.py
│   │   ├── mapper.py
│   │   ├── cis_azure.py
│   │   ├── nist_800_53.py
│   │   ├── soc2.py
│   │   └── iso27001.py
│   ├── reports/
│   │   ├── pdf_generator.py       # Existing, enhance
│   │   ├── word_generator.py      # NEW
│   │   ├── branding.py            # NEW: White-label support
│   │   └── templates/             # NEW: Report templates
│   └── services/
│       └── graph_client.py        # Existing
├── brands/                         # NEW: Brand configs
│   ├── operationmos/
│   │   ├── config.json
│   │   └── logo.svg
│   └── default/
│       └── config.json
└── data/
    └── frameworks/                 # Existing
        ├── cis_azure_v2.json
        ├── nist_800_53.json
        ├── soc2_criteria.json
        └── iso27001_annex_a.json
```
