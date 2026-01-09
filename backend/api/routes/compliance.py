"""
Compliance API routes for Azure Security Platform V2

Provides framework mapping, control status, and compliance reporting.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel


router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class ComplianceControl(BaseModel):
    """A single compliance control"""
    control_id: str
    title: str
    description: str
    status: str  # "pass", "fail", "partial", "not_applicable"
    category: str
    frameworks: List[str]  # e.g., ["SOC 2", "ISO 27001"]
    evidence_available: bool
    last_assessed: datetime


class FrameworkSummary(BaseModel):
    """Summary for a compliance framework"""
    framework_id: str
    framework_name: str
    version: str
    total_controls: int
    passing_controls: int
    failing_controls: int
    partial_controls: int
    not_applicable: int
    compliance_percent: float
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
# Mock Data
# ============================================================================

def get_mock_controls() -> List[ComplianceControl]:
    """Generate mock compliance controls"""
    return [
        ComplianceControl(
            control_id="AC-001",
            title="Multi-Factor Authentication Required",
            description="All users must authenticate using MFA for all applications",
            status="partial",
            category="Access Control",
            frameworks=["SOC 2", "ISO 27001", "CIS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="AC-002",
            title="Privileged Access Management",
            description="Privileged accounts use just-in-time activation",
            status="pass",
            category="Access Control",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="AC-003",
            title="Conditional Access Policies",
            description="Risk-based conditional access policies are enforced",
            status="pass",
            category="Access Control",
            frameworks=["SOC 2", "CIS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="DP-001",
            title="Data Encryption at Rest",
            description="All sensitive data is encrypted using AES-256",
            status="pass",
            category="Data Protection",
            frameworks=["SOC 2", "ISO 27001", "PCI-DSS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="DP-002",
            title="Data Encryption in Transit",
            description="All data in transit uses TLS 1.2+",
            status="pass",
            category="Data Protection",
            frameworks=["SOC 2", "ISO 27001", "PCI-DSS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="BC-001",
            title="Backup Frequency",
            description="Critical systems backed up at least daily",
            status="pass",
            category="Business Continuity",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="BC-002",
            title="Backup Testing",
            description="Backup restoration tested quarterly",
            status="partial",
            category="Business Continuity",
            frameworks=["SOC 2", "ISO 27001"],
            evidence_available=False,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="IR-001",
            title="Incident Response Plan",
            description="Documented incident response procedures",
            status="pass",
            category="Incident Response",
            frameworks=["SOC 2", "ISO 27001", "NIST"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="VM-001",
            title="Vulnerability Scanning",
            description="Regular vulnerability scanning of all systems",
            status="pass",
            category="Vulnerability Mgmt",
            frameworks=["SOC 2", "CIS", "PCI-DSS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
        ComplianceControl(
            control_id="VM-002",
            title="Patch Management SLA",
            description="Critical patches applied within 7 days",
            status="fail",
            category="Vulnerability Mgmt",
            frameworks=["SOC 2", "CIS"],
            evidence_available=True,
            last_assessed=datetime.utcnow(),
        ),
    ]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/frameworks")
async def list_frameworks(tenant_id: str):
    """
    List available compliance frameworks with summary stats.
    """
    controls = get_mock_controls()
    
    frameworks = {
        "SOC 2": {"name": "SOC 2 Type II", "version": "2017"},
        "ISO 27001": {"name": "ISO/IEC 27001", "version": "2022"},
        "CIS": {"name": "CIS Azure Benchmark", "version": "2.0"},
        "PCI-DSS": {"name": "PCI DSS", "version": "4.0"},
        "NIST": {"name": "NIST CSF", "version": "2.0"},
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
        total = len(fw_controls)
        
        summaries.append(FrameworkSummary(
            framework_id=fw_id,
            framework_name=fw_info["name"],
            version=fw_info["version"],
            total_controls=total,
            passing_controls=passing,
            failing_controls=failing,
            partial_controls=partial,
            not_applicable=na,
            compliance_percent=round((passing / total) * 100, 1) if total > 0 else 0,
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
    controls = get_mock_controls()
    
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
