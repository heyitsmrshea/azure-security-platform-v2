# Persona Gap Features Implementation Plan

**Status:** IN_PROGRESS  
**Created:** 2026-01-09  
**Last Updated:** 2026-01-09  

## Overview

This plan addresses the feature gaps identified from the 5 user personas:
- **Marcus (CISO):** Needs health grades, export, simplified language
- **Sarah (Analyst):** Needs bulk actions, department views
- **David (MSP):** Needs multi-tenant overview, tenant switcher
- **Jennifer (Compliance):** Needs framework mapping, evidence export
- **Rachel (HR):** Needs simplified view, offboarding verification

---

## Phase 1: Quick Wins

### 1.1 Health Grade [IN_PROGRESS]
- **Status:** IN_PROGRESS
- **Files:**
  - [NEW] `frontend/src/components/executive/HealthGrade.tsx`
  - [MODIFY] `frontend/src/app/[tenantId]/executive/page.tsx`

### 1.2 Connected Export [PENDING]
- **Status:** PENDING
- **Files:**
  - [NEW] `frontend/src/components/shared/ExportModal.tsx`
  - [MODIFY] `frontend/src/components/shared/DashboardHeader.tsx`

### 1.3 Simplified View Mode [PENDING]
- **Status:** PENDING
- **Files:**
  - [NEW] `frontend/src/lib/simple-labels.ts`
  - [NEW] `frontend/src/hooks/useViewMode.ts`
  - [MODIFY] `frontend/src/components/shared/DashboardHeader.tsx`

---

## Phase 2: Core Gaps

### 2.1 Bulk Actions [PENDING]
- **Files:**
  - [NEW] `frontend/src/components/it-staff/BulkActionBar.tsx`
  - [MODIFY] `frontend/src/components/it-staff/DataTable.tsx`

### 2.2 Department Breakdowns [PENDING]
- **Files:**
  - [NEW] `frontend/src/components/it-staff/DepartmentBreakdown.tsx`
  - [MODIFY] `backend/api/routes/it_staff.py`
  - [MODIFY] `frontend/src/lib/api-client.ts`

### 2.3 Tenant Switcher [PENDING]
- **Files:**
  - [NEW] `frontend/src/context/TenantContext.tsx`
  - [NEW] `frontend/src/components/shared/TenantSwitcher.tsx`
  - [MODIFY] `frontend/src/components/shared/DashboardHeader.tsx`

---

## Phase 3: Advanced Features

### 3.1 Multi-Tenant Overview [PENDING]
- **Files:**
  - [NEW] `backend/api/routes/msp.py`
  - [MODIFY] `backend/api/main.py`
  - [NEW] `frontend/src/app/msp/overview/page.tsx`
  - [NEW] `frontend/src/components/msp/TenantRankingTable.tsx`
  - [MODIFY] `frontend/src/lib/api-client.ts`

### 3.2 Framework Mapping [PENDING]
- **Files:**
  - [NEW] `frontend/src/app/[tenantId]/compliance/page.tsx`
  - [NEW] `frontend/src/components/compliance/ControlMapping.tsx`
  - [NEW] `backend/api/routes/compliance.py`
  - [MODIFY] `backend/api/main.py`

---

## Phase 4: Compliance Features

### 4.1 Offboarding View [PENDING]
- **Files:**
  - [NEW] `frontend/src/components/it-staff/OffboardingStatus.tsx`

### 4.2 Evidence Export [PENDING]
- **Files:**
  - [NEW] `frontend/src/components/compliance/EvidenceExport.tsx`
  - [NEW] `backend/reports/evidence_generator.py`
  - [MODIFY] `backend/api/routes/reports.py`

---

## Notes

- All features use dark theme only (slate backgrounds, red/orange/yellow/blue severity)
- Typography: Inter font, 48px KPIs, 20px headers, 12px labels
- No gradients, emojis, excessive animations, or stock photos
