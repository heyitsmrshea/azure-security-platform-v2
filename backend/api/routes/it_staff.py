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
import structlog

from models.schemas import (
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
from services.live_data_service import get_live_data_service
from services.azure_client import get_azure_client

router = APIRouter()
logger = structlog.get_logger(__name__)


def is_real_tenant(tenant_id: str) -> bool:
    """Check if this is a real tenant (not demo) that should use live data."""
    demo_tenants = {"demo", "acme-corp", "globex", "initech"}
    return tenant_id.lower() not in demo_tenants


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
    
    Uses live Azure Defender data for real tenants, mock data for demo tenants.
    """
    now = datetime.utcnow()
    alerts = []
    
    # Try to get live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            live_data = await live_service.get_security_alerts()
            
            if live_data.get("is_live") and live_data.get("alerts"):
                for alert in live_data["alerts"]:
                    # Map severity from Azure format
                    sev_str = str(alert.get("severity", "")).lower()
                    if "high" in sev_str:
                        sev = Severity.HIGH
                    elif "medium" in sev_str:
                        sev = Severity.MEDIUM
                    elif "low" in sev_str:
                        sev = Severity.LOW
                    else:
                        sev = Severity.INFO
                    
                    # Map status
                    status_str = str(alert.get("status", "")).lower()
                    if "resolved" in status_str:
                        mapped_status = "resolved"
                    elif "inprogress" in status_str:
                        mapped_status = "investigating"
                    else:
                        mapped_status = "active"
                    
                    # Parse created_at safely
                    created_at = now
                    if alert.get("created_at"):
                        try:
                            ca = alert["created_at"]
                            if isinstance(ca, str):
                                created_at = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                            elif isinstance(ca, datetime):
                                created_at = ca
                        except Exception:
                            pass
                    
                    alerts.append(SecurityAlert(
                        id=alert.get("id", "unknown"),
                        title=alert.get("title", "Unknown Alert"),
                        description=alert.get("description", ""),
                        severity=sev,
                        status=mapped_status,
                        category=alert.get("category", "Unknown"),
                        resource_name=alert.get("service_source", "Azure"),
                        resource_type="Cloud Service",
                        created_at=created_at,
                    ))
                logger.info("loaded_live_alerts", tenant_id=tenant_id, count=len(alerts))
                return AlertsResponse(
                    items=alerts,
                    total=len(alerts),
                    page=page,
                    page_size=page_size,
                    has_more=False
                )
        except Exception as e:
            logger.error("live_alerts_fetch_failed", error=str(e), tenant_id=tenant_id)
            # For real tenants, return empty list on error explicitly - NO MOCK FALLBACK
            return AlertsResponse(items=[], total=0, page=page, page_size=page_size, has_more=False)
            
    # Mock data strictly for demo tenants
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
    
    NOTE: Vulnerability data requires Microsoft Defender for Endpoint API,
    which is separate from Microsoft Graph API. This endpoint currently
    returns mock data. To implement live data, would need:
    - Defender for Endpoint P2 license
    - Separate API integration for /api/vulnerabilities endpoint
    - Additional authentication setup
    
    Includes CVE details, severity, age, and remediation info.
    """
    now = datetime.utcnow()
    
    # Strictly return empty for real tenants as this requires distinct integration not yet built
    if is_real_tenant(tenant_id):
        return VulnerabilitiesResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            has_more=False,
            summary={"critical": 0, "high": 0, "medium": 0, "low": 0}
        )

    # Demo Mock Data
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
    gaps = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            if live_service._graph_client:
                users = await live_service._graph_client.get_mfa_registration_details()
                
                for user in users:
                    if not user.get("is_mfa_registered"):
                        gaps.append(MFAGap(
                            user_id=user.get("id", "unknown"),
                            display_name=user.get("display_name", "Unknown User"),
                            email=user.get("user_principal_name", ""),
                            department=user.get("department", "Unknown"),
                            is_admin=user.get("is_admin", False),
                            last_sign_in=now - timedelta(days=1),  # Placeholder - would need sign-in logs
                        ))
                logger.info("loaded_live_mfa_gaps", tenant_id=tenant_id, count=len(gaps))
                return gaps
        except Exception as e:
            logger.error("live_mfa_gaps_fetch_failed", error=str(e), tenant_id=tenant_id)
            
        # Return whatever we have (empty or partial), do NOT fallback to mock for real tenants
        return gaps
    
    # Mock fallback only for demo
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
    policies = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            ca_data = await live_service.get_conditional_access_policies()
            
            if ca_data.get("is_live") and ca_data.get("policies"):
                for policy in ca_data["policies"]:
                    # Parse dates safely
                    created_at = now - timedelta(days=90)
                    if policy.get("created_at"):
                        try:
                            ca = policy["created_at"]
                            if isinstance(ca, str):
                                created_at = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                            elif isinstance(ca, datetime):
                                created_at = ca
                        except Exception:
                            pass
                    
                    modified_at = None
                    if policy.get("modified_at"):
                        try:
                            ma = policy["modified_at"]
                            if isinstance(ma, str):
                                modified_at = datetime.fromisoformat(ma.replace("Z", "+00:00"))
                            elif isinstance(ma, datetime):
                                modified_at = ma
                        except Exception:
                            pass
                    
                    policies.append(ConditionalAccessPolicy(
                        id=policy.get("id", "unknown"),
                        name=policy.get("name", "Unknown Policy"),
                        state=policy.get("state", "disabled"),
                        grant_controls=policy.get("grant_controls", []),
                        conditions=policy.get("conditions", {}),
                        created_at=created_at,
                        modified_at=modified_at,
                    ))
                logger.info("loaded_live_ca_policies", tenant_id=tenant_id, count=len(policies))
                return policies
        except Exception as e:
            logger.error("live_ca_policies_fetch_failed", error=str(e), tenant_id=tenant_id)
        
        # Return real results (empty or not), no mock fallback
        return policies
    
    # Mock fallback for demo only
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
    priv_users = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            if live_service._graph_client:
                assignments = await live_service._graph_client.get_directory_role_assignments()
                roles = await live_service._graph_client.get_directory_roles()
                users = await live_service._graph_client.get_mfa_registration_details()
                
                # Build role ID to name mapping
                role_map = {r.get("id"): r.get("display_name", "Unknown") for r in roles}
                
                # Build user ID to user info mapping
                user_map = {u.get("id"): u for u in users}
                
                # Group assignments by principal
                principal_roles = {}
                for a in assignments:
                    pid = a.get("principal_id")
                    rid = a.get("role_definition_id")
                    if pid not in principal_roles:
                        principal_roles[pid] = []
                    role_name = role_map.get(rid, "Unknown Role")
                    if role_name not in principal_roles[pid]:
                        principal_roles[pid].append(role_name)
                
                # Create PrivilegedUser entries
                for pid, role_list in principal_roles.items():
                    user_info = user_map.get(pid, {})
                    priv_users.append(PrivilegedUser(
                        user_id=pid,
                        display_name=user_info.get("display_name", "Unknown User"),
                        email=user_info.get("user_principal_name", ""),
                        roles=role_list,
                        is_pim_eligible=False,  # Would need PIM API
                        is_pim_active=True,
                        last_activity=now - timedelta(hours=1),  # Placeholder
                        mfa_enabled=user_info.get("is_mfa_registered", False),
                    ))
                
                logger.info("loaded_live_privileged_users", tenant_id=tenant_id, count=len(priv_users))
                return priv_users
        except Exception as e:
            logger.error("live_privileged_users_fetch_failed", error=str(e), tenant_id=tenant_id)
        
        return priv_users
    
    # Mock fallback for demo
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
    risky_signins = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            signin_data = await live_service.get_risky_sign_ins_data(days)
            
            if signin_data.get("is_live") and signin_data.get("detections"):
                for detection in signin_data["detections"]:
                    # Parse timestamp
                    signin_time = now
                    if detection.get("detected_datetime"):
                        try:
                            dt = detection["detected_datetime"]
                            if isinstance(dt, str):
                                signin_time = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                            elif isinstance(dt, datetime):
                                signin_time = dt
                        except Exception:
                            pass
                    
                    risky_signins.append(RiskySignIn(
                        id=detection.get("id", "unknown"),
                        user_id=detection.get("user_id", "unknown"),
                        display_name=detection.get("user_display_name", "Unknown User"),
                        email=detection.get("user_principal_name", ""),
                        risk_level=detection.get("risk_level", "none"),
                        risk_detail=detection.get("risk_detail", "Unknown"),
                        location=detection.get("location", "Unknown"),
                        ip_address=detection.get("ip_address", "Unknown"),
                        app_display_name=detection.get("activity", "Unknown App"),
                        sign_in_time=signin_time,
                    ))
                logger.info("loaded_live_risky_signins", tenant_id=tenant_id, count=len(risky_signins))
                return risky_signins
        except Exception as e:
            logger.error("live_risky_signins_fetch_failed", error=str(e), tenant_id=tenant_id)
        
        return risky_signins
    
    # Mock fallback for demo
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
    devices = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            device_data = await live_service.get_device_compliance()
            
            if device_data.get("is_live") and device_data.get("devices"):
                for d in device_data["devices"]:
                    # Only include non-compliant devices
                    if d.get("compliance_state", "").lower() == "noncompliant":
                        # Parse last check-in date
                        last_check = now
                        if d.get("last_sync_datetime"):
                            try:
                                ls = d["last_sync_datetime"]
                                if isinstance(ls, str):
                                    last_check = datetime.fromisoformat(ls.replace("Z", "+00:00"))
                                elif isinstance(ls, datetime):
                                    last_check = ls
                            except Exception:
                                pass
                        
                        devices.append(NonCompliantDevice(
                            device_id=d.get("id", "unknown"),
                            device_name=d.get("device_name", "Unknown Device"),
                            os_type=d.get("operating_system", "Unknown"),
                            os_version=d.get("os_version", "Unknown"),
                            owner=d.get("user_principal_name", "Unknown"),
                            compliance_state=d.get("compliance_state", "noncompliant"),
                            failure_reasons=d.get("compliance_issues", ["Non-compliant"]),
                            last_check_in=last_check,
                        ))
                logger.info("loaded_live_noncompliant_devices", tenant_id=tenant_id, count=len(devices))
        except Exception as e:
            logger.error("live_devices_fetch_failed", error=str(e), tenant_id=tenant_id)
    
    # Mock fallback only if not real tenant (for real tenant, return empty if failed/none)
    if not is_real_tenant(tenant_id) and not devices:
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
    guests = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            if live_service._graph_client:
                live_guests = await live_service._graph_client.get_guest_users()
                
                for g in live_guests:
                    created = g.get("created_datetime")
                    if created:
                        try:
                            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        except:
                            created_dt = now - timedelta(days=30)
                    else:
                        created_dt = now - timedelta(days=30)
                    
                    guests.append(GuestUser(
                        user_id=g.get("id", "unknown"),
                        display_name=g.get("display_name", "Guest User"),
                        email=g.get("mail") or g.get("user_principal_name", ""),
                        source="B2B" if "#EXT#" in g.get("user_principal_name", "") else "Invited",
                        created_at=created_dt,
                        last_sign_in=now - timedelta(days=7),  # Placeholder
                        access_level="Guest Access",
                    ))
                
                logger.info("loaded_live_guest_users", tenant_id=tenant_id, count=len(guests))
                return guests
        except Exception as e:
            logger.error("live_guest_users_fetch_failed", error=str(e), tenant_id=tenant_id)
            
        return guests
    
    # Mock fallback for demo
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
    apps = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            app_data = await live_service.get_third_party_apps_data()
            
            if app_data.get("is_live") and app_data.get("apps"):
                for app in app_data["apps"]:
                    # Parse consent date
                    consented_at = now - timedelta(days=90)
                    if app.get("consented_at"):
                        try:
                            ca = app["consented_at"]
                            if isinstance(ca, str):
                                consented_at = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                            elif isinstance(ca, datetime):
                                consented_at = ca
                        except Exception:
                            pass
                    
                    apps.append(ThirdPartyApp(
                        app_id=app.get("app_id", "unknown"),
                        display_name=app.get("display_name", "Unknown App"),
                        publisher=app.get("publisher_name", "Unknown Publisher"),
                        permissions=app.get("permissions", []),
                        consent_type=app.get("consent_type", "user"),
                        consented_by=app.get("consented_by", "Unknown"),
                        consented_at=consented_at,
                    ))
                logger.info("loaded_live_third_party_apps", tenant_id=tenant_id, count=len(apps))
                return apps
        except Exception as e:
            logger.error("live_third_party_apps_fetch_failed", error=str(e), tenant_id=tenant_id)
            
        return apps
    
    # Mock fallback for demo
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
    """
    Get backup job status for all protected items.
    
    NOTE: Backup job data requires Azure Backup ARM API, which is separate
    from Microsoft Graph API. This endpoint currently returns mock data.
    To implement live data, would need:
    - Azure Backup configuration
    - ARM API integration (not Graph API)
    - Access to Recovery Services Vaults
    """
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
    logs = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            if live_service._graph_client:
                audit_data = await live_service._graph_client.get_directory_audit_logs(days)
                
                for log in audit_data:
                    # Parse timestamp
                    timestamp = now
                    if log.get("timestamp"):
                        try:
                            ts = log["timestamp"]
                            if isinstance(ts, str):
                                timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            elif isinstance(ts, datetime):
                                timestamp = ts
                        except Exception:
                            pass
                    
                    # Format target resources
                    target_resource = "Unknown"
                    if log.get("target_resources"):
                        targets = log["target_resources"]
                        if targets:
                            target = targets[0]
                            target_resource = f"{target.get('type', 'Resource')}: {target.get('display_name', 'Unknown')}"
                    
                    logs.append(AuditLogEntry(
                        id=log.get("id", "unknown"),
                        activity=log.get("activity", "Unknown Activity"),
                        category=log.get("category", "Unknown"),
                        initiated_by=log.get("initiated_by", "Unknown"),
                        target_resource=target_resource,
                        result=log.get("result", "unknown"),
                        timestamp=timestamp,
                        details={},
                    ))
                logger.info("loaded_live_audit_logs", tenant_id=tenant_id, count=len(logs))
        except Exception as e:
            logger.error("live_audit_logs_fetch_failed", error=str(e), tenant_id=tenant_id)
    
    # Mock fallback
    if not logs:
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
    operations = []
    
    # Try live data for real tenants
    if is_real_tenant(tenant_id):
        try:
            live_service = get_live_data_service()
            ops_data = await live_service.get_high_risk_operations(days)
            
            if ops_data.get("is_live") and ops_data.get("operations"):
                for op in ops_data["operations"]:
                    # Parse timestamp
                    timestamp = now
                    if op.get("timestamp"):
                        try:
                            ts = op["timestamp"]
                            if isinstance(ts, str):
                                timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            elif isinstance(ts, datetime):
                                timestamp = ts
                        except Exception:
                            pass
                    
                    target = "Unknown"
                    if op.get("target_resources"):
                        targets = op["target_resources"]
                        if targets:
                            target = targets[0].get("display_name", "Unknown")
                    
                    operations.append({
                        "operation": op.get("activity", "Unknown Operation"),
                        "initiated_by": op.get("initiated_by", "Unknown"),
                        "target": target,
                        "timestamp": timestamp,
                        "risk_reason": op.get("category", "High-risk operation"),
                    })
                logger.info("loaded_live_high_risk_ops", tenant_id=tenant_id, count=len(operations))
                return operations
        except Exception as e:
            logger.error("live_high_risk_ops_fetch_failed", error=str(e), tenant_id=tenant_id)
    
    # Mock fallback
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


@router.get("/analytics/departments")
async def get_department_analytics(tenant_id: str):
    """
    Get departmental breakdowns of security metrics.
    """
    if not is_real_tenant(tenant_id):
        # Return mock data for demo tenants so the UI isn't empty
        return {
            "mfa_by_department": [
                {"department": "Engineering", "total": 45, "compliant": 42, "nonCompliant": 3, "percentage": 93.3},
                {"department": "Sales", "total": 30, "compliant": 18, "nonCompliant": 12, "percentage": 60.0},
                {"department": "Marketing", "total": 22, "compliant": 20, "nonCompliant": 2, "percentage": 90.9},
                {"department": "HR", "total": 15, "compliant": 14, "nonCompliant": 1, "percentage": 93.3},
            ],
            "devices_by_department": [
                {"department": "Engineering", "total": 45, "compliant": 44, "nonCompliant": 1, "percentage": 97.8},
                {"department": "Sales", "total": 30, "compliant": 25, "nonCompliant": 5, "percentage": 83.3},
                {"department": "Marketing", "total": 22, "compliant": 15, "nonCompliant": 7, "percentage": 68.2},
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    try:
        live_service = get_live_data_service()
        if not live_service.is_connected():
            return {
                "mfa_by_department": [],
                "devices_by_department": [],
                "error": "Live service not connected"
            }
            
        data = await live_service.get_department_analytics()
        
        return {
            "mfa_by_department": data.get("mfa_by_department", []),
            "devices_by_department": data.get("devices_by_department", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("department_analytics_endpoint_failed", error=str(e))
        return {
            "mfa_by_department": [],
            "devices_by_department": [],
            "error": str(e)
        }

