"""
IT Staff Dashboard API routes for Azure Security Platform V2

Provides detailed operational data for IT staff including:
- Alerts & Incidents
- Vulnerability Management
- Identity & Access details
- Device Security
- Third-Party/Vendor Risk
- Backup & Recovery details
- Audit Trail
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...models.schemas import (
    SecurityAlert,
    Vulnerability,
    MFAGap,
    ConditionalAccessPolicy,
    PrivilegedUser,
    RiskySignIn,
    NonCompliantDevice,
    GuestUser,
    ThirdPartyApp,
    BackupJob,
    AuditLogEntry,
    Severity,
    PaginatedResponse,
)

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class AlertsResponse(BaseModel):
    items: list[SecurityAlert]
    total: int
    page: int
    page_size: int
    has_more: bool


class VulnerabilitiesResponse(BaseModel):
    items: list[Vulnerability]
    total: int
    page: int
    page_size: int
    has_more: bool
    summary: dict


class DevicesResponse(BaseModel):
    items: list[NonCompliantDevice]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Alerts & Incidents
# ============================================================================

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    tenant_id: str,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
):
    """
    Get security alerts with filtering.
    
    Sortable/filterable list with severity, age, resource.
    """
    now = datetime.utcnow()
    
    # Mock data - in production would query from cache/cosmos
    alerts = [
        SecurityAlert(
            id="alert-001",
            title="Suspicious sign-in activity detected",
            description="Multiple failed sign-in attempts followed by successful login from unusual location",
            severity=Severity.HIGH,
            status="active",
            category="Identity",
            resource_name="john.doe@company.com",
            resource_type="User",
            created_at=now - timedelta(hours=2),
        ),
        SecurityAlert(
            id="alert-002",
            title="Malware detected on device",
            description="Windows Defender detected and quarantined malicious file",
            severity=Severity.MEDIUM,
            status="resolved",
            category="Endpoint",
            resource_name="DESKTOP-ABC123",
            resource_type="Device",
            created_at=now - timedelta(hours=8),
            updated_at=now - timedelta(hours=6),
        ),
        SecurityAlert(
            id="alert-003",
            title="Unusual resource access pattern",
            description="User accessed 50+ files in SharePoint within 5 minutes",
            severity=Severity.MEDIUM,
            status="investigating",
            category="Data",
            resource_name="Marketing Documents",
            resource_type="SharePoint Site",
            created_at=now - timedelta(hours=12),
        ),
    ]
    
    # Filter by severity if specified
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity.lower()]
    
    # Filter by status if specified
    if status:
        alerts = [a for a in alerts if a.status == status.lower()]
    
    total = len(alerts)
    start = (page - 1) * page_size
    end = start + page_size
    
    return AlertsResponse(
        items=alerts[start:end],
        total=total,
        page=page,
        page_size=page_size,
        has_more=end < total,
    )


# ============================================================================
# Vulnerability Management
# ============================================================================

@router.get("/vulnerabilities", response_model=VulnerabilitiesResponse)
async def get_vulnerabilities(
    tenant_id: str,
    severity: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
):
    """
    Get vulnerabilities with filtering.
    
    Includes CVE details, severity, age, and remediation info.
    """
    now = datetime.utcnow()
    
    vulnerabilities = [
        Vulnerability(
            id="vuln-001",
            cve_id="CVE-2024-1234",
            title="Remote Code Execution in Windows Server",
            description="A remote code execution vulnerability exists in Windows Server",
            severity=Severity.CRITICAL,
            cvss_score=9.8,
            affected_resource="SQL-SERVER-01",
            resource_type="Virtual Machine",
            first_seen=now - timedelta(days=3),
            status="open",
            remediation="Apply KB5001234 security update",
        ),
        Vulnerability(
            id="vuln-002",
            cve_id="CVE-2024-5678",
            title="Privilege Escalation in Azure AD Connect",
            description="Local privilege escalation vulnerability in AD Connect sync service",
            severity=Severity.HIGH,
            cvss_score=7.8,
            affected_resource="ADCONNECT-01",
            resource_type="Server",
            first_seen=now - timedelta(days=7),
            status="in_progress",
            remediation="Upgrade to AD Connect version 2.1.x",
        ),
        Vulnerability(
            id="vuln-003",
            cve_id="CVE-2024-9012",
            title="Information Disclosure in IIS",
            description="IIS may disclose sensitive information in error messages",
            severity=Severity.MEDIUM,
            cvss_score=5.3,
            affected_resource="WEB-SERVER-01",
            resource_type="Virtual Machine",
            first_seen=now - timedelta(days=14),
            status="open",
            remediation="Configure custom error pages",
        ),
    ]
    
    summary = {
        "critical": len([v for v in vulnerabilities if v.severity == Severity.CRITICAL]),
        "high": len([v for v in vulnerabilities if v.severity == Severity.HIGH]),
        "medium": len([v for v in vulnerabilities if v.severity == Severity.MEDIUM]),
        "low": len([v for v in vulnerabilities if v.severity == Severity.LOW]),
    }
    
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity.value == severity.lower()]
    
    total = len(vulnerabilities)
    start = (page - 1) * page_size
    end = start + page_size
    
    return VulnerabilitiesResponse(
        items=vulnerabilities[start:end],
        total=total,
        page=page,
        page_size=page_size,
        has_more=end < total,
        summary=summary,
    )


# ============================================================================
# Identity & Access
# ============================================================================

@router.get("/mfa-gaps", response_model=list[MFAGap])
async def get_mfa_gaps(tenant_id: str):
    """Get users without MFA by department."""
    now = datetime.utcnow()
    
    return [
        MFAGap(
            user_id="user-001",
            display_name="Jane Smith",
            email="jane.smith@company.com",
            department="Marketing",
            is_admin=False,
            last_sign_in=now - timedelta(days=1),
        ),
        MFAGap(
            user_id="user-002",
            display_name="Bob Wilson",
            email="bob.wilson@company.com",
            department="Sales",
            is_admin=False,
            last_sign_in=now - timedelta(days=3),
        ),
    ]


@router.get("/conditional-access", response_model=list[ConditionalAccessPolicy])
async def get_conditional_access_policies(tenant_id: str):
    """Get Conditional Access policies and coverage gaps."""
    now = datetime.utcnow()
    
    return [
        ConditionalAccessPolicy(
            id="ca-001",
            name="Require MFA for admins",
            state="enabled",
            grant_controls=["mfa"],
            conditions={
                "users": {"include": ["All admins"]},
                "applications": {"include": ["All"]},
            },
            created_at=now - timedelta(days=90),
            modified_at=now - timedelta(days=30),
        ),
        ConditionalAccessPolicy(
            id="ca-002",
            name="Block legacy authentication",
            state="enabled",
            grant_controls=["block"],
            conditions={
                "users": {"include": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"],
            },
            created_at=now - timedelta(days=60),
        ),
        ConditionalAccessPolicy(
            id="ca-003",
            name="Require compliant device for Office 365",
            state="enabledForReportingButNotEnforced",
            grant_controls=["compliantDevice"],
            conditions={
                "users": {"include": ["All"]},
                "applications": {"include": ["Office 365"]},
            },
            created_at=now - timedelta(days=14),
        ),
    ]


@router.get("/privileged-users", response_model=list[PrivilegedUser])
async def get_privileged_users(tenant_id: str):
    """Get all users with privileged roles."""
    now = datetime.utcnow()
    
    return [
        PrivilegedUser(
            user_id="admin-001",
            display_name="IT Admin",
            email="it.admin@company.com",
            roles=["Global Administrator"],
            is_pim_eligible=False,
            is_pim_active=True,
            last_activity=now - timedelta(hours=1),
            mfa_enabled=True,
        ),
        PrivilegedUser(
            user_id="admin-002",
            display_name="Security Admin",
            email="security.admin@company.com",
            roles=["Security Administrator", "Compliance Administrator"],
            is_pim_eligible=True,
            is_pim_active=False,
            last_activity=now - timedelta(days=2),
            mfa_enabled=True,
        ),
        PrivilegedUser(
            user_id="admin-003",
            display_name="User Admin",
            email="user.admin@company.com",
            roles=["User Administrator"],
            is_pim_eligible=True,
            is_pim_active=True,
            last_activity=now - timedelta(hours=6),
            mfa_enabled=True,
        ),
    ]


@router.get("/risky-signins", response_model=list[RiskySignIn])
async def get_risky_signins(tenant_id: str, days: int = Query(default=7, le=30)):
    """Get recent risky sign-in events."""
    now = datetime.utcnow()
    
    return [
        RiskySignIn(
            id="signin-001",
            user_id="user-005",
            display_name="Alex Johnson",
            email="alex.johnson@company.com",
            risk_level="medium",
            risk_detail="Unfamiliar sign-in properties",
            location="Moscow, Russia",
            ip_address="185.x.x.x",
            app_display_name="Office 365",
            sign_in_time=now - timedelta(hours=4),
        ),
        RiskySignIn(
            id="signin-002",
            user_id="user-008",
            display_name="Sarah Chen",
            email="sarah.chen@company.com",
            risk_level="low",
            risk_detail="Atypical travel",
            location="London, UK",
            ip_address="51.x.x.x",
            app_display_name="Azure Portal",
            sign_in_time=now - timedelta(hours=12),
        ),
    ]


# ============================================================================
# Device Security
# ============================================================================

@router.get("/non-compliant-devices", response_model=DevicesResponse)
async def get_non_compliant_devices(
    tenant_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
):
    """Get non-compliant devices with failure reasons."""
    now = datetime.utcnow()
    
    devices = [
        NonCompliantDevice(
            device_id="device-001",
            device_name="LAPTOP-XYZ789",
            os_type="Windows",
            os_version="10.0.19044",
            owner="john.doe@company.com",
            compliance_state="noncompliant",
            failure_reasons=["Firewall disabled", "Antivirus out of date"],
            last_check_in=now - timedelta(hours=2),
        ),
        NonCompliantDevice(
            device_id="device-002",
            device_name="DESKTOP-ABC456",
            os_type="Windows",
            os_version="10.0.19041",
            owner="jane.smith@company.com",
            compliance_state="noncompliant",
            failure_reasons=["OS version outdated"],
            last_check_in=now - timedelta(days=1),
        ),
    ]
    
    total = len(devices)
    start = (page - 1) * page_size
    end = start + page_size
    
    return DevicesResponse(
        items=devices[start:end],
        total=total,
        page=page,
        page_size=page_size,
        has_more=end < total,
    )


# ============================================================================
# Third-Party/Vendor Risk
# ============================================================================

@router.get("/guest-users", response_model=list[GuestUser])
async def get_guest_users(tenant_id: str):
    """Get guest/external users with access levels."""
    now = datetime.utcnow()
    
    return [
        GuestUser(
            user_id="guest-001",
            display_name="External Consultant",
            email="consultant@partner.com",
            source="Invited",
            created_at=now - timedelta(days=45),
            last_sign_in=now - timedelta(days=30),
            access_level="Member of 3 Teams",
        ),
        GuestUser(
            user_id="guest-002",
            display_name="Vendor Contact",
            email="support@vendor.com",
            source="B2B",
            created_at=now - timedelta(days=120),
            last_sign_in=now - timedelta(days=95),
            access_level="SharePoint site access",
        ),
    ]


@router.get("/third-party-apps", response_model=list[ThirdPartyApp])
async def get_third_party_apps(tenant_id: str):
    """Get third-party apps with admin consent."""
    now = datetime.utcnow()
    
    return [
        ThirdPartyApp(
            app_id="app-001",
            display_name="Slack",
            publisher="Slack Technologies",
            permissions=["User.Read", "Calendars.Read"],
            consent_type="admin",
            consented_by="IT Admin",
            consented_at=now - timedelta(days=180),
        ),
        ThirdPartyApp(
            app_id="app-002",
            display_name="Zoom",
            publisher="Zoom Video Communications",
            permissions=["User.Read", "OnlineMeetings.ReadWrite"],
            consent_type="admin",
            consented_by="IT Admin",
            consented_at=now - timedelta(days=90),
        ),
        ThirdPartyApp(
            app_id="app-003",
            display_name="Unknown App",
            publisher="Unknown Publisher",
            permissions=["Mail.Read", "Files.ReadWrite.All"],
            consent_type="user",
            consented_by="john.doe@company.com",
            consented_at=now - timedelta(days=7),
        ),
    ]


# ============================================================================
# Backup & Recovery
# ============================================================================

@router.get("/backup-jobs", response_model=list[BackupJob])
async def get_backup_jobs(tenant_id: str, days: int = Query(default=7, le=30)):
    """Get backup job status for all protected items."""
    now = datetime.utcnow()
    
    return [
        BackupJob(
            job_id="job-001",
            protected_item="SQL-SERVER-01",
            vault_name="prod-backup-vault",
            status="Completed",
            start_time=now - timedelta(hours=4),
            end_time=now - timedelta(hours=3, minutes=45),
            duration_minutes=15,
        ),
        BackupJob(
            job_id="job-002",
            protected_item="FILE-SERVER-01",
            vault_name="prod-backup-vault",
            status="Completed",
            start_time=now - timedelta(hours=5),
            end_time=now - timedelta(hours=4, minutes=30),
            duration_minutes=30,
        ),
        BackupJob(
            job_id="job-003",
            protected_item="WEB-SERVER-01",
            vault_name="prod-backup-vault",
            status="Failed",
            start_time=now - timedelta(hours=6),
            end_time=now - timedelta(hours=5, minutes=55),
            duration_minutes=5,
            error_message="Insufficient disk space on backup target",
        ),
    ]


@router.get("/unprotected-assets")
async def get_unprotected_assets(tenant_id: str):
    """Get critical systems without backup protection."""
    return [
        {
            "name": "DEV-SERVER-03",
            "type": "Virtual Machine",
            "criticality": "medium",
            "reason": "Not configured for backup",
        },
        {
            "name": "TEST-DB-01",
            "type": "SQL Database",
            "criticality": "low",
            "reason": "Excluded from backup policy",
        },
    ]


# ============================================================================
# Audit Trail
# ============================================================================

@router.get("/audit-logs", response_model=list[AuditLogEntry])
async def get_audit_logs(
    tenant_id: str,
    category: Optional[str] = None,
    days: int = Query(default=7, le=30),
):
    """Get recent admin actions and high-risk operations."""
    now = datetime.utcnow()
    
    logs = [
        AuditLogEntry(
            id="audit-001",
            activity="Add member to role",
            category="RoleManagement",
            initiated_by="IT Admin",
            target_resource="User: john.doe@company.com",
            result="success",
            timestamp=now - timedelta(hours=2),
            details={"role": "Security Reader"},
        ),
        AuditLogEntry(
            id="audit-002",
            activity="Update conditional access policy",
            category="Policy",
            initiated_by="Security Admin",
            target_resource="Policy: Require MFA for admins",
            result="success",
            timestamp=now - timedelta(hours=6),
            details={"change": "Added exclusion group"},
        ),
        AuditLogEntry(
            id="audit-003",
            activity="Delete user",
            category="UserManagement",
            initiated_by="HR System",
            target_resource="User: former.employee@company.com",
            result="success",
            timestamp=now - timedelta(hours=12),
        ),
        AuditLogEntry(
            id="audit-004",
            activity="Consent to application",
            category="ApplicationManagement",
            initiated_by="john.doe@company.com",
            target_resource="App: Unknown App",
            result="success",
            timestamp=now - timedelta(days=1),
            details={"permissions": ["Mail.Read", "Files.ReadWrite.All"]},
        ),
    ]
    
    if category:
        logs = [l for l in logs if l.category.lower() == category.lower()]
    
    return logs


@router.get("/high-risk-operations")
async def get_high_risk_operations(tenant_id: str, days: int = Query(default=7, le=30)):
    """Get sensitive/high-risk admin operations."""
    now = datetime.utcnow()
    
    return [
        {
            "operation": "Global Admin role assigned",
            "initiated_by": "IT Admin",
            "target": "new.admin@company.com",
            "timestamp": now - timedelta(days=3),
            "risk_reason": "Highly privileged role assignment",
        },
        {
            "operation": "Conditional Access policy disabled",
            "initiated_by": "Security Admin",
            "target": "Block legacy auth policy",
            "timestamp": now - timedelta(days=5),
            "risk_reason": "Security control disabled",
        },
    ]
