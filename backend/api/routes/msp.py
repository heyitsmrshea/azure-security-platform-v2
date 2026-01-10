"""
MSP (Managed Service Provider) API routes for Azure Security Platform V2

Provides multi-tenant overview and cross-tenant management capabilities for MSPs.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel


router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class TenantSummary(BaseModel):
    """Summary metrics for a single tenant"""
    tenant_id: str
    tenant_name: str
    security_score: float
    compliance_score: float
    critical_risks: int
    high_risks: int
    mfa_coverage_percent: float
    device_compliance_percent: float
    backup_health_percent: float
    active_alerts: int
    status: str  # "healthy", "warning", "critical"
    last_updated: datetime


class MSPOverview(BaseModel):
    """Aggregated overview across all tenants"""
    total_tenants: int
    healthy_tenants: int
    warning_tenants: int
    critical_tenants: int
    average_security_score: float
    average_compliance_score: float
    total_critical_risks: int
    total_high_risks: int
    total_active_alerts: int
    tenants: List[TenantSummary]
    generated_at: datetime


from models.schemas import (
    Tenant, 
    SecurityScore,
    ComplianceScore,
    AlertSummary,
    RiskSummary
)
from services.tenant_manager import TenantManager
from services.live_data_service import get_live_data_service


class CrossTenantAlert(BaseModel):
    """Alert that appears across multiple tenants"""
    alert_id: str
    title: str
    severity: str
    affected_tenants: List[str]
    tenant_count: int
    recommendation: str
    created_at: datetime


# ============================================================================
# Mock Data
# ============================================================================

def generate_mock_tenants() -> List[TenantSummary]:
    """Generate mock tenant data for demo purposes"""
    tenants = [
        TenantSummary(
            tenant_id="demo",
            tenant_name="Demo Organization",
            security_score=72.5,
            compliance_score=68.5,
            critical_risks=3,
            high_risks=12,
            mfa_coverage_percent=87.3,
            device_compliance_percent=92.8,
            backup_health_percent=94.5,
            active_alerts=5,
            status="warning",
            last_updated=datetime.utcnow(),
        ),
        TenantSummary(
            tenant_id="acme-corp",
            tenant_name="Acme Corporation",
            security_score=85.2,
            compliance_score=82.1,
            critical_risks=0,
            high_risks=5,
            mfa_coverage_percent=98.5,
            device_compliance_percent=95.3,
            backup_health_percent=100.0,
            active_alerts=2,
            status="healthy",
            last_updated=datetime.utcnow(),
        ),
        TenantSummary(
            tenant_id="globex",
            tenant_name="Globex Industries",
            security_score=58.1,
            compliance_score=52.3,
            critical_risks=8,
            high_risks=22,
            mfa_coverage_percent=62.1,
            device_compliance_percent=71.5,
            backup_health_percent=78.0,
            active_alerts=15,
            status="critical",
            last_updated=datetime.utcnow(),
        ),
        TenantSummary(
            tenant_id="initech",
            tenant_name="Initech Solutions",
            security_score=91.0,
            compliance_score=88.5,
            critical_risks=0,
            high_risks=2,
            mfa_coverage_percent=100.0,
            device_compliance_percent=98.1,
            backup_health_percent=100.0,
            active_alerts=0,
            status="healthy",
            last_updated=datetime.utcnow(),
        ),
        TenantSummary(
            tenant_id="umbrella",
            tenant_name="Umbrella Corp",
            security_score=67.3,
            compliance_score=61.2,
            critical_risks=2,
            high_risks=15,
            mfa_coverage_percent=78.5,
            device_compliance_percent=85.2,
            backup_health_percent=88.0,
            active_alerts=8,
            status="warning",
            last_updated=datetime.utcnow(),
        ),
    ]
    return tenants


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/overview", response_model=MSPOverview)
async def get_msp_overview():
    """
    Get aggregated overview of all managed tenants.
    
    Returns summary metrics, risk counts, and per-tenant details ranked by risk.
    """
    tenants = generate_mock_tenants()
    
    # Calculate aggregates
    total = len(tenants)
    healthy = sum(1 for t in tenants if t.status == "healthy")
    warning = sum(1 for t in tenants if t.status == "warning")
    critical = sum(1 for t in tenants if t.status == "critical")
    
    avg_security = sum(t.security_score for t in tenants) / total
    avg_compliance = sum(t.compliance_score for t in tenants) / total
    
    total_critical = sum(t.critical_risks for t in tenants)
    total_high = sum(t.high_risks for t in tenants)
    total_alerts = sum(t.active_alerts for t in tenants)
    
    # Sort by status (critical first) then by score (lowest first)
    status_order = {"critical": 0, "warning": 1, "healthy": 2}
    sorted_tenants = sorted(tenants, key=lambda t: (status_order.get(t.status, 3), t.security_score))
    
    return MSPOverview(
        total_tenants=total,
        healthy_tenants=healthy,
        warning_tenants=warning,
        critical_tenants=critical,
        average_security_score=round(avg_security, 1),
        average_compliance_score=round(avg_compliance, 1),
        total_critical_risks=total_critical,
        total_high_risks=total_high,
        total_active_alerts=total_alerts,
        tenants=sorted_tenants,
        generated_at=datetime.utcnow(),
    )


@router.get("/tenants")
async def list_tenants(
    status: Optional[str] = None,
    sort_by: str = Query(default="security_score", pattern="^(security_score|compliance_score|name|status)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    """
    List all managed tenants with optional filtering and sorting.
    """
    tenants = generate_mock_tenants()
    
    # Filter by status
    if status:
        tenants = [t for t in tenants if t.status == status]
    
    # Sort
    reverse = sort_order == "desc"
    if sort_by == "name":
        tenants = sorted(tenants, key=lambda t: t.tenant_name.lower(), reverse=reverse)
    elif sort_by == "status":
        status_order = {"critical": 0, "warning": 1, "healthy": 2}
        tenants = sorted(tenants, key=lambda t: status_order.get(t.status, 3), reverse=reverse)
    else:
        tenants = sorted(tenants, key=lambda t: getattr(t, sort_by, 0), reverse=reverse)
    
    return {
        "tenants": tenants,
        "total": len(tenants),
    }


@router.get("/alerts")
async def get_cross_tenant_alerts(
    severity: Optional[str] = None,
    limit: int = Query(default=10, le=50),
):
    """
    Get priority alerts across all tenants.
    
    Shows alerts affecting multiple tenants or high-severity alerts.
    """
    # Mock cross-tenant alerts
    alerts = [
        CrossTenantAlert(
            alert_id="xta-001",
            title="Legacy Authentication Still Enabled",
            severity="high",
            affected_tenants=["demo", "globex", "umbrella"],
            tenant_count=3,
            recommendation="Disable legacy authentication in Conditional Access policies",
            created_at=datetime.utcnow(),
        ),
        CrossTenantAlert(
            alert_id="xta-002",
            title="Critical Patches Overdue",
            severity="critical",
            affected_tenants=["globex"],
            tenant_count=1,
            recommendation="Apply critical security patches within 7 days",
            created_at=datetime.utcnow(),
        ),
        CrossTenantAlert(
            alert_id="xta-003",
            title="MFA Coverage Below 80%",
            severity="high",
            affected_tenants=["globex", "umbrella"],
            tenant_count=2,
            recommendation="Enforce MFA for all users",
            created_at=datetime.utcnow(),
        ),
        CrossTenantAlert(
            alert_id="xta-004",
            title="Backup Failures Detected",
            severity="medium",
            affected_tenants=["globex"],
            tenant_count=1,
            recommendation="Investigate and resolve backup job failures",
            created_at=datetime.utcnow(),
        ),
    ]
    
    # Filter by severity
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    return {
        "alerts": alerts[:limit],
        "total": len(alerts),
    }


@router.get("/comparison")
async def compare_tenants(
    tenant_ids: str = Query(..., description="Comma-separated tenant IDs to compare"),
):
    """
    Compare metrics across selected tenants.
    """
    ids = [id.strip() for id in tenant_ids.split(",")]
    tenants = generate_mock_tenants()
    
    selected = [t for t in tenants if t.tenant_id in ids]
    
    if not selected:
        return {"error": "No matching tenants found"}
    
    return {
        "tenants": selected,
        "comparison": {
            "security_score": {
                "min": min(t.security_score for t in selected),
                "max": max(t.security_score for t in selected),
                "avg": sum(t.security_score for t in selected) / len(selected),
            },
            "mfa_coverage": {
                "min": min(t.mfa_coverage_percent for t in selected),
                "max": max(t.mfa_coverage_percent for t in selected),
                "avg": sum(t.mfa_coverage_percent for t in selected) / len(selected),
            },
        },
    }
