"""
Compliance API routes for Azure Security Platform V2

Provides framework mapping, control status, and compliance reporting.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel
import structlog

from services.live_data_service import get_live_data_service

router = APIRouter()
logger = structlog.get_logger(__name__)


def is_real_tenant(tenant_id: str) -> bool:
    """Check if this is a real tenant (not demo) that should use live data."""
    demo_tenants = {"demo", "acme-corp", "globex", "initech"}
    return tenant_id.lower() not in demo_tenants


# ============================================================================
# Models
# ============================================================================

class ComplianceControl(BaseModel):
    """A single compliance control"""
    control_id: str
    title: str
    description: str
    status: str  # "pass", "fail", "partial", "not_applicable", "unknown"
    status_reason: str = ""  # Human-readable explanation of why this status
    category: str
    frameworks: List[str]  # e.g., ["SOC 2", "ISO 27001"]
    evidence_available: bool
    data_source: str = ""  # What API/data was used for assessment
    last_assessed: datetime


class FrameworkSummary(BaseModel):
    """Summary for a compliance framework"""
    id: str  # Matches frontend expectation
    name: str  # Matches frontend expectation  
    lookup: str  # Used for filtering controls
    description: str = ""
    version: str
    controls_total: int  # Matches frontend expectation
    controls_passed: int  # Matches frontend expectation
    compliance_percent: float
    # Additional detail fields
    passing: int  # Matches frontend expectation
    failing: int  # Matches frontend expectation
    partial: int  # Matches frontend expectation
    not_applicable: int
    unknown: int = 0  # Controls that couldn't be assessed
    last_updated: datetime


class ControlMapping(BaseModel):
    """Mapping between controls and frameworks"""
    control_id: str
    control_title: str
    soc2_ref: Optional[str] = None
    iso27001_ref: Optional[str] = None
    cis_ref: Optional[str] = None
    nist_ref: Optional[str] = None


# ============================================================================
# Data Logic
# ============================================================================

async def get_controls(tenant_id: str) -> List[ComplianceControl]:
    """
    Get compliance controls with status.
    
    For real tenants, calculates status based on live security data.
    For demo tenants, returns static mock data.
    """
    now = datetime.utcnow()
    
    # Base controls definition (the "Standard")
    # Each control starts with unknown status until we can verify
    controls = [
        ComplianceControl(
            control_id="AC-001",
            title="Multi-Factor Authentication Required",
            description="All users must authenticate using MFA for all applications",
            status="unknown",
            status_reason="Not yet assessed",
            category="Access Control",
            frameworks=["SOC 2", "ISO 27001", "CIS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="AC-002",
            title="Privileged Access Management",
            description="Privileged accounts use just-in-time access (PIM)",
            status="unknown",
            status_reason="Not yet assessed",
            category="Access Control",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="AC-003",
            title="Conditional Access Policies",
            description="Risk-based conditional access policies are enforced",
            status="unknown",
            status_reason="Not yet assessed",
            category="Access Control",
            frameworks=["SOC 2", "CIS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="DP-001",
            title="Data Encryption at Rest",
            description="All sensitive data is encrypted using AES-256",
            status="unknown",
            status_reason="Not yet assessed",
            category="Data Protection",
            frameworks=["SOC 2", "ISO 27001", "PCI-DSS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="DP-002",
            title="Data Encryption in Transit",
            description="All data in transit uses TLS 1.2+",
            status="unknown",
            status_reason="Not yet assessed",
            category="Data Protection",
            frameworks=["SOC 2", "ISO 27001", "PCI-DSS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="BC-001",
            title="Backup Frequency",
            description="Critical systems backed up at least daily",
            status="unknown",
            status_reason="Not yet assessed",
            category="Business Continuity",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="BC-002",
            title="Backup Testing",
            description="Backup restoration tested quarterly",
            status="unknown",
            status_reason="Not yet assessed",
            category="Business Continuity",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="IR-001",
            title="Incident Response Plan",
            description="Documented incident response procedures",
            status="unknown",
            status_reason="Not yet assessed",
            category="Incident Response",
            frameworks=["SOC 2", "ISO 27001", "NIST"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="VM-001",
            title="Vulnerability Scanning",
            description="Microsoft Defender for Cloud vulnerability assessment enabled",
            status="unknown",
            status_reason="Not yet assessed",
            category="Vulnerability Mgmt",
            frameworks=["SOC 2", "CIS", "PCI-DSS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
        ComplianceControl(
            control_id="VM-002",
            title="Patch Management SLA",
            description="Critical patches applied within 7 days",
            status="unknown",
            status_reason="Not yet assessed",
            category="Vulnerability Mgmt",
            frameworks=["SOC 2", "CIS"],
            evidence_available=False,
            data_source="",
            last_assessed=now,
        ),
    ]

    # If demo tenant, set demo status reasons
    if not is_real_tenant(tenant_id):
        for c in controls:
            c.status = "pass" if c.control_id in ["DP-001", "DP-002", "VM-001"] else "partial"
            c.status_reason = "Demo data - not from live tenant"
            c.data_source = "Mock data"
            c.evidence_available = True
        return controls

    # ============================================================================
    # Live Data Calculation - with clear status reasons
    # ============================================================================
    try:
        live_service = get_live_data_service()
        if not live_service.is_connected():
            logger.error("compliance_service_not_connected", tenant_id=tenant_id)
            for c in controls:
                c.status_reason = "Unable to connect to Azure APIs"
            return controls

        # 1. Fetch MFA Data for AC-001
        mfa_stats = await live_service.get_mfa_coverage()
        ac_001 = next((c for c in controls if c.control_id == "AC-001"), None)
        if ac_001:
            if mfa_stats.get("is_live"):
                users_count = mfa_stats.get("total_users", 0)
                users_with_mfa = mfa_stats.get("users_with_mfa", 0)
                coverage_pct = round((users_with_mfa / users_count * 100), 1) if users_count > 0 else 0
                
                ac_001.data_source = "Microsoft Graph: Authentication Methods"
                if users_count > 0:
                    if coverage_pct >= 95:
                        ac_001.status = "pass"
                        ac_001.status_reason = f"{coverage_pct}% MFA coverage ({users_with_mfa}/{users_count} users)"
                    elif coverage_pct >= 70:
                        ac_001.status = "partial"
                        ac_001.status_reason = f"{coverage_pct}% MFA coverage - {users_count - users_with_mfa} users without MFA"
                    else:
                        ac_001.status = "fail"
                        ac_001.status_reason = f"Only {coverage_pct}% MFA coverage - {users_count - users_with_mfa} users at risk"
                    ac_001.evidence_available = True
                else:
                    ac_001.status_reason = "No users found in tenant"
            else:
                ac_001.status_reason = "MFA data unavailable - check API permissions"

        # 2. Fetch Conditional Access for AC-003
        ca_stats = await live_service.get_conditional_access_policies()
        ac_003 = next((c for c in controls if c.control_id == "AC-003"), None)
        if ac_003:
            if ca_stats.get("is_live"):
                policies = ca_stats.get("policies", [])
                enabled_policies = [p for p in policies if p.get("state") == "enabled"]
                total_policies = len(policies)
                enabled_count = len(enabled_policies)
                
                ac_003.data_source = "Microsoft Graph: Conditional Access"
                if enabled_count >= 2:
                    ac_003.status = "pass"
                    ac_003.status_reason = f"{enabled_count} CA policies enabled (of {total_policies} total)"
                elif enabled_count > 0:
                    ac_003.status = "partial"
                    ac_003.status_reason = f"Only {enabled_count} CA policy enabled - consider additional policies"
                else:
                    ac_003.status = "fail"
                    ac_003.status_reason = f"No Conditional Access policies enabled ({total_policies} defined but disabled)"
                ac_003.evidence_available = True
            else:
                ac_003.status_reason = "Conditional Access data unavailable - check API permissions"

        # 3. Fetch Privileged Accounts for AC-002
        priv_data = await live_service.get_privileged_accounts()
        ac_002 = next((c for c in controls if c.control_id == "AC-002"), None)
        if ac_002:
            if priv_data.get("is_live"):
                global_admins = priv_data.get("global_admin_count", 0)
                pim_eligible = priv_data.get("pim_eligible_count", 0)
                
                ac_002.data_source = "Microsoft Graph: Directory Roles"
                if global_admins <= 2 and pim_eligible > 0:
                    ac_002.status = "pass"
                    ac_002.status_reason = f"{global_admins} Global Admins, {pim_eligible} using PIM"
                elif global_admins <= 5:
                    ac_002.status = "partial"
                    reason_parts = [f"{global_admins} Global Admins"]
                    if pim_eligible == 0:
                        reason_parts.append("PIM not in use")
                    else:
                        reason_parts.append(f"{pim_eligible} using PIM")
                    ac_002.status_reason = " - ".join(reason_parts)
                else:
                    ac_002.status = "fail"
                    ac_002.status_reason = f"Too many Global Admins ({global_admins}) - best practice is ≤2"
                ac_002.evidence_available = True
            else:
                ac_002.status_reason = "Privileged account data unavailable - check API permissions"

        # 4. Data Encryption Controls - Azure Platform Defaults
        # These are always-on for Azure services but we should be honest about limitations
        dp_001 = next((c for c in controls if c.control_id == "DP-001"), None)
        dp_002 = next((c for c in controls if c.control_id == "DP-002"), None)
        
        if dp_001:
            dp_001.status = "pass"
            dp_001.status_reason = "Azure Storage Service Encryption enabled by default"
            dp_001.data_source = "Azure Platform Default"
            dp_001.evidence_available = False  # No API evidence, platform guarantee
        
        if dp_002:
            dp_002.status = "pass"
            dp_002.status_reason = "TLS 1.2+ enforced by Azure platform"
            dp_002.data_source = "Azure Platform Default"
            dp_002.evidence_available = False  # No API evidence, platform guarantee

        # 5. Vulnerability Scanning (VM-001) - Use Secure Score as indicator
        score_data = await live_service.get_secure_score()
        vm_001 = next((c for c in controls if c.control_id == "VM-001"), None)
        if vm_001:
            if score_data.get("is_live"):
                score_percent = score_data.get("score_percent", 0)
                
                vm_001.data_source = "Microsoft Secure Score"
                # Check if Defender recommendations exist (would indicate vuln scanning)
                controls_list = score_data.get("controls", [])
                defender_controls = [c for c in controls_list if "defender" in c.get("name", "").lower()]
                
                if score_percent > 50 and len(defender_controls) > 0:
                    vm_001.status = "pass"
                    vm_001.status_reason = f"Secure Score {score_percent:.0f}% with Defender enabled"
                elif score_percent > 30:
                    vm_001.status = "partial"
                    vm_001.status_reason = f"Secure Score {score_percent:.0f}% - consider enabling more Defender features"
                else:
                    vm_001.status = "fail"
                    vm_001.status_reason = f"Low Secure Score ({score_percent:.0f}%) indicates gaps in vulnerability detection"
                vm_001.evidence_available = True
            else:
                vm_001.status_reason = "Secure Score data unavailable - check API permissions"

        # 6. Patch Management (VM-002) - Use Device Compliance as indicator
        device_data = await live_service.get_device_compliance()
        vm_002 = next((c for c in controls if c.control_id == "VM-002"), None)
        if vm_002:
            if device_data.get("is_live"):
                compliance_percent = device_data.get("compliance_percent", 0)
                total_devices = device_data.get("total_devices", 0)
                non_compliant = device_data.get("non_compliant_count", 0)
                unknown_count = device_data.get("unknown_count", 0)
                
                vm_002.data_source = "Microsoft Intune: Device Compliance"
                
                if total_devices == 0:
                    vm_002.status = "unknown"
                    vm_002.status_reason = "No managed devices found in Intune"
                elif unknown_count == total_devices:
                    vm_002.status = "unknown"
                    vm_002.status_reason = f"{total_devices} devices pending compliance evaluation"
                elif compliance_percent >= 95:
                    vm_002.status = "pass"
                    vm_002.status_reason = f"{compliance_percent:.0f}% device compliance ({total_devices} devices)"
                elif compliance_percent >= 80:
                    vm_002.status = "partial"
                    vm_002.status_reason = f"{compliance_percent:.0f}% compliant - {non_compliant} devices need attention"
                else:
                    vm_002.status = "fail"
                    vm_002.status_reason = f"Only {compliance_percent:.0f}% compliant - {non_compliant} devices non-compliant"
                vm_002.evidence_available = True
            else:
                vm_002.status_reason = "Device compliance data unavailable - check Intune permissions"

        # 7. Backup Controls - Require Azure Backup integration
        bc_001 = next((c for c in controls if c.control_id == "BC-001"), None)
        bc_002 = next((c for c in controls if c.control_id == "BC-002"), None)
        
        if bc_001:
            bc_001.status = "unknown"
            bc_001.status_reason = "Azure Backup API integration not configured"
            bc_001.data_source = "Not connected"
            bc_001.evidence_available = False
        
        if bc_002:
            bc_002.status = "unknown"
            bc_002.status_reason = "Requires manual attestation - backup test logs needed"
            bc_002.data_source = "Manual Process"
            bc_002.evidence_available = False

        # 8. Incident Response (IR-001) - Check for alert monitoring capability
        alerts_data = await live_service.get_security_alerts()
        ir_001 = next((c for c in controls if c.control_id == "IR-001"), None)
        if ir_001:
            if alerts_data.get("is_live"):
                total_alerts = alerts_data.get("total_alerts", 0)
                active_alerts = alerts_data.get("active_alerts", 0)
                
                ir_001.data_source = "Microsoft Graph: Security Alerts"
                # Having alerts visible = monitoring is in place
                # But we can't verify documented procedures via API
                ir_001.status = "partial"
                ir_001.status_reason = f"Alert monitoring active ({active_alerts} active of {total_alerts}) - documented procedures need manual verification"
                ir_001.evidence_available = True
            else:
                ir_001.status_reason = "Security alerts data unavailable - check API permissions"

        logger.info("compliance_scores_calculated", tenant_id=tenant_id, 
                   controls_evaluated=len([c for c in controls if c.status != "unknown"]))

    except Exception as e:
        logger.error("compliance_calculation_failed", error=str(e), tenant_id=tenant_id)
        for c in controls:
            c.status_reason = f"Assessment error: {str(e)[:50]}"
        
    return controls


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/frameworks")
async def list_frameworks(tenant_id: str):
    """
    List available compliance frameworks with summary stats.
    """
    controls = await get_controls(tenant_id)
    
    frameworks = {
        "SOC 2": {"name": "SOC 2 Type II", "desc": "Service Organization Controls for security, availability, and confidentiality", "version": "2017"},
        "ISO 27001": {"name": "ISO/IEC 27001", "desc": "Information security management system standard", "version": "2022"},
        "CIS": {"name": "CIS Azure Benchmark", "desc": "Center for Internet Security best practices for Azure", "version": "2.0"},
        "PCI-DSS": {"name": "PCI DSS", "desc": "Payment Card Industry Data Security Standard", "version": "4.0"},
        "NIST": {"name": "NIST CSF", "desc": "Cybersecurity Framework from National Institute of Standards", "version": "2.0"},
    }
    
    summaries = []
    for fw_id, fw_info in frameworks.items():
        fw_controls = [c for c in controls if fw_id in c.frameworks]
        if not fw_controls:
            continue
            
        passing = sum(1 for c in fw_controls if c.status == "pass")
        failing = sum(1 for c in fw_controls if c.status == "fail")
        partial = sum(1 for c in fw_controls if c.status == "partial")
        na = sum(1 for c in fw_controls if c.status == "not_applicable")
        unknown = sum(1 for c in fw_controls if c.status == "unknown")
        total = len(fw_controls)
        
        # Calculate compliance: only count pass/total (exclude unknown from denominator for fair %)
        assessed = total - unknown
        compliance_pct = round((passing / assessed) * 100, 1) if assessed > 0 else 0
        
        summaries.append(FrameworkSummary(
            id=fw_id,  # Frontend expects 'id'
            name=fw_info["name"],  # Frontend expects 'name'
            lookup=fw_id,  # Used to filter controls
            description=fw_info["desc"],
            version=fw_info["version"],
            controls_total=total,  # Frontend expects 'controls_total'
            controls_passed=passing,  # Frontend expects 'controls_passed'
            compliance_percent=compliance_pct,
            passing=passing,  # Frontend expects 'passing'
            failing=failing,  # Frontend expects 'failing'
            partial=partial,  # Frontend expects 'partial'
            not_applicable=na,
            unknown=unknown,
            last_updated=datetime.utcnow(),
        ))
    
    return {"frameworks": summaries}


@router.get("/controls")
async def list_controls(
    tenant_id: str,
    framework: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    List compliance controls with optional filtering.
    """
    controls = await get_controls(tenant_id)
    
    if framework:
        controls = [c for c in controls if framework in c.frameworks]
    if status:
        controls = [c for c in controls if c.status == status]
    if category:
        controls = [c for c in controls if c.category == category]
    
    # Group by category
    categories = {}
    for control in controls:
        if control.category not in categories:
            categories[control.category] = []
        categories[control.category].append(control)
    
    return {
        "controls": controls,
        "by_category": categories,
        "total": len(controls),
        "summary": {
            "pass": sum(1 for c in controls if c.status == "pass"),
            "fail": sum(1 for c in controls if c.status == "fail"),
            "partial": sum(1 for c in controls if c.status == "partial"),
        }
    }


@router.get("/mapping")
async def get_control_mapping(tenant_id: str):
    """
    Get control-to-framework mapping matrix.
    """
    mappings = [
        ControlMapping(control_id="AC-001", control_title="Multi-Factor Authentication", soc2_ref="CC6.1", iso27001_ref="A.9.4.2", cis_ref="1.1.1"),
        ControlMapping(control_id="AC-002", control_title="Privileged Access Management", soc2_ref="CC6.2", iso27001_ref="A.9.2.3"),
        ControlMapping(control_id="AC-003", control_title="Conditional Access Policies", soc2_ref="CC6.1", cis_ref="1.1.4"),
        ControlMapping(control_id="DP-001", control_title="Data Encryption at Rest", soc2_ref="CC6.7", iso27001_ref="A.10.1.1"),
        ControlMapping(control_id="DP-002", control_title="Data Encryption in Transit", soc2_ref="CC6.7", iso27001_ref="A.13.1.1"),
        ControlMapping(control_id="BC-001", control_title="Backup Frequency", soc2_ref="A1.2", iso27001_ref="A.12.3.1"),
        ControlMapping(control_id="BC-002", control_title="Backup Testing", soc2_ref="A1.2", iso27001_ref="A.12.3.1"),
        ControlMapping(control_id="IR-001", control_title="Incident Response Plan", soc2_ref="CC7.3", iso27001_ref="A.16.1.1", nist_ref="RS.RP-1"),
        ControlMapping(control_id="VM-001", control_title="Vulnerability Scanning", soc2_ref="CC7.1", cis_ref="7.1"),
        ControlMapping(control_id="VM-002", control_title="Patch Management SLA", soc2_ref="CC7.1", cis_ref="7.3"),
    ]
    
    return {"mappings": mappings}


@router.get("/evidence/{control_id}")
async def get_control_evidence(tenant_id: str, control_id: str):
    """
    Get evidence for a specific control.
    """
@router.get("/evidence/{control_id}")
async def get_control_evidence(tenant_id: str, control_id: str):
    """
    Get evidence for a specific control.
    """
    if is_real_tenant(tenant_id):
        # We do not have live evidence collection yet
        return {
            "control_id": control_id,
            "evidence": [],
            "last_updated": datetime.utcnow().isoformat(),
        }

    # Mock evidence
    return {
        "control_id": control_id,
        "evidence": [
            {
                "type": "configuration",
                "title": "Azure AD MFA Policy Configuration",
                "collected_at": datetime.utcnow().isoformat(),
                "status": "valid",
            },
            {
                "type": "log",
                "title": "MFA Enrollment Report",
                "collected_at": datetime.utcnow().isoformat(),
                "status": "valid",
            },
        ],
        "last_updated": datetime.utcnow().isoformat(),
    }
