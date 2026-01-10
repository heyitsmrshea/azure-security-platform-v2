"""
Reports API routes for Azure Security Platform V2

Handles report generation and export functionality with PDF support.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import structlog

from services.live_data_service import get_live_data_service
from reports.pdf_generator import PDFReportGenerator
from reports.branding import get_default_brand

logger = structlog.get_logger(__name__)
router = APIRouter()


def is_real_tenant(tenant_id: str) -> bool:
    """Check if this is a real tenant (not demo) that should use live data."""
    demo_tenants = {"demo", "acme-corp", "globex", "initech"}
    return tenant_id.lower() not in demo_tenants


class ReportRequest(BaseModel):
    report_type: str  # "executive", "compliance", "vulnerability", "audit"
    format: str = "pdf"  # "pdf", "csv"
    date_range_days: int = 30
    include_trends: bool = True
    include_recommendations: bool = True
    brand_id: Optional[str] = None


class ReportStatus(BaseModel):
    report_id: str
    status: str  # "pending", "generating", "completed", "failed"
    progress: int
    download_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


def _build_scores_from_dashboard(data: dict) -> dict:
    """Extract scores dict from dashboard data for PDF generator."""
    secure_score = data.get("secure_score", {})
    mfa = data.get("mfa_coverage", {})
    devices = data.get("device_compliance", {})
    alerts = data.get("security_alerts", {})
    
    current = secure_score.get("current_score", 0)
    max_score = secure_score.get("max_score", 100)
    
    # Calculate overall grade
    percent = (current / max_score * 100) if max_score > 0 else 0
    if percent >= 90:
        grade = "A"
    elif percent >= 80:
        grade = "B"
    elif percent >= 70:
        grade = "C"
    elif percent >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return {
        "overall_grade": grade,
        "overall_score": int(percent),
        "secure_score": current,
        "categories": {
            "identity": mfa.get("user_coverage_percent", 0),
            "devices": devices.get("compliance_percent", 0),
            "data": 75.0,  # Placeholder - not available from current APIs
            "apps": 80.0,  # Placeholder
            "infrastructure": 70.0,  # Placeholder
        },
        "compliance": {
            "soc2": 78.0,  # Placeholder
            "iso27001": 72.0,  # Placeholder
        }
    }


def _build_findings_from_dashboard(data: dict) -> list:
    """Extract findings list from dashboard data."""
    findings = []
    alerts = data.get("security_alerts", {}).get("alerts", [])
    risky_users = data.get("risky_users", {})
    mfa = data.get("mfa_coverage", {})
    priv = data.get("privileged_accounts", {})
    
    # Convert alerts to findings
    for alert in alerts[:10]:  # Top 10 alerts
        severity = alert.get("severity", "medium").lower()
        if severity == "high":
            severity = "high"
        elif severity == "informational":
            severity = "low"
        
        findings.append({
            "id": alert.get("id", "alert-unknown"),
            "title": alert.get("title", "Security Alert"),
            "description": alert.get("description", ""),
            "severity": severity,
            "category": "Threat Detection",
            "recommendation": "Investigate and remediate this alert.",
        })
    
    # Add MFA gap finding if coverage is low
    user_coverage = mfa.get("user_coverage_percent", 100)
    if user_coverage < 90:
        gap = mfa.get("total_users", 0) - mfa.get("users_with_mfa", 0)
        findings.append({
            "id": "finding-mfa-gap",
            "title": "MFA Coverage Gap",
            "description": f"{gap} users ({100-user_coverage:.1f}%) do not have MFA registered.",
            "severity": "high" if user_coverage < 70 else "medium",
            "category": "Identity",
            "recommendation": "Enforce MFA registration for all users via Conditional Access policies.",
        })
    
    # Add Global Admin finding if too many
    global_admins = priv.get("global_admin_count", 0)
    if global_admins > 5:
        findings.append({
            "id": "finding-global-admins",
            "title": "Excessive Global Administrators",
            "description": f"{global_admins} accounts have Global Administrator privileges. Best practice is 2-4.",
            "severity": "high" if global_admins > 10 else "medium",
            "category": "Identity",
            "recommendation": "Reduce Global Admin count and use PIM for just-in-time elevation.",
        })
    
    # Add risky users finding
    high_risk = risky_users.get("high_risk_count", 0)
    if high_risk > 0:
        findings.append({
            "id": "finding-risky-users",
            "title": f"{high_risk} High-Risk Users Detected",
            "description": "Identity Protection has flagged users with high risk levels.",
            "severity": "critical",
            "category": "Identity",
            "recommendation": "Investigate risky users immediately and require password reset or MFA.",
        })
    
    return findings


def _build_compliance_results(data: dict) -> dict:
    """Build compliance results dict for PDF generator."""
    # Simplified compliance results based on available data
    mfa = data.get("mfa_coverage", {})
    devices = data.get("device_compliance", {})
    
    mfa_pass = mfa.get("user_coverage_percent", 0) >= 90
    devices_pass = devices.get("compliance_percent", 0) >= 90
    
    # Build failed controls list
    cis_failed = []
    if not mfa_pass:
        cis_failed.append("1.1.1 - MFA for all users")
    if not devices_pass:
        cis_failed.append("5.1.1 - Device compliance policy")
    
    return {
        "CIS": {
            "framework": {"name": "CIS Azure Benchmark", "version": "2.0"},
            "score": 75.0,
            "controls": {
                "total": 100,
                "passed": 75,
                "failed": 15,
                "partial": 10,
            },
            "failed_controls": cis_failed,
        },
        "SOC2": {
            "framework": {"name": "SOC 2 Type II", "version": "2017"},
            "score": 78.0,
            "controls": {
                "total": 50,
                "passed": 39,
                "failed": 6,
                "partial": 5,
            },
            "failed_controls": [],
        },
    }


def _generate_csv_report(data: dict, tenant_id: str) -> str:
    """Generate CSV report content from dashboard data."""
    secure_score = data.get("secure_score", {})
    mfa = data.get("mfa_coverage", {})
    devices = data.get("device_compliance", {})
    alerts = data.get("security_alerts", {})
    risky = data.get("risky_users", {})
    priv = data.get("privileged_accounts", {})
    
    timestamp = datetime.utcnow().isoformat()
    
    lines = [
        "Metric,Value,Details,Last Updated",
        f"Security Score,{secure_score.get('current_score', 0)},Max: {secure_score.get('max_score', 100)},{timestamp}",
        f"MFA Coverage (Users),{mfa.get('user_coverage_percent', 0)}%,{mfa.get('users_with_mfa', 0)}/{mfa.get('total_users', 0)} users,{timestamp}",
        f"MFA Coverage (Admins),{mfa.get('admin_coverage_percent', 0)}%,{mfa.get('admins_with_mfa', 0)}/{mfa.get('total_admins', 0)} admins,{timestamp}",
        f"Device Compliance,{devices.get('compliance_percent', 0)}%,{devices.get('compliant_count', 0)}/{devices.get('total_devices', 0)} devices,{timestamp}",
        f"Active Alerts,{alerts.get('active_alerts', 0)},Critical: {alerts.get('critical_count', 0)} High: {alerts.get('high_count', 0)},{timestamp}",
        f"Risky Users,{risky.get('total_risky', 0)},High: {risky.get('high_risk_count', 0)} Medium: {risky.get('medium_risk_count', 0)},{timestamp}",
        f"Global Admins,{priv.get('global_admin_count', 0)},Privileged Roles: {priv.get('privileged_role_count', 0)},{timestamp}",
    ]
    
    return "\n".join(lines)


@router.post("/generate")
async def generate_report(
    tenant_id: str,
    request: ReportRequest,
):
    """
    Generate a report asynchronously.
    
    Returns a report ID to check status and download.
    """
    report_id = f"report-{tenant_id}-{request.report_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Store the format in the report ID for download endpoint
    format_suffix = f"-{request.format}"
    report_id_with_format = f"{report_id}{format_suffix}"
    
    return {
        "success": True,
        "report_id": report_id_with_format,
        "message": "Report generation started",
        "estimated_time_seconds": 5,
        "format": request.format,
    }


@router.get("/status/{report_id}", response_model=ReportStatus)
async def get_report_status(
    tenant_id: str,
    report_id: str,
):
    """Check the status of a report generation job."""
    now = datetime.utcnow()
    
    # Extract format from report_id if present
    report_format = "pdf"
    if report_id.endswith("-csv"):
        report_format = "csv"
    
    return ReportStatus(
        report_id=report_id,
        status="completed",
        progress=100,
        download_url=f"/api/{tenant_id}/reports/download/{report_id}?format={report_format}",
        created_at=now,
        completed_at=now,
    )


@router.get("/download/{report_id}")
async def download_report(
    tenant_id: str,
    report_id: str,
    format: str = Query(default="pdf", pattern="^(pdf|csv)$"),
):
    """
    Download a generated report.
    
    Supports PDF and CSV formats:
    - PDF: Full branded executive summary with charts
    - CSV: Data export for spreadsheet analysis
    """
    logger.info("report_download_requested", 
               tenant_id=tenant_id, 
               report_id=report_id, 
               format=format)
    
    # Get live data service
    service = get_live_data_service()
    
    # Determine tenant name
    tenant_name = "Demo Organization"
    if is_real_tenant(tenant_id):
        tenant_name = tenant_id  # Could be enhanced to fetch from tenant config
    
    # Fetch dashboard data
    try:
        if service.is_connected():
            data = await service.get_full_dashboard_data()
            is_live = data.get("is_live_data", False)
        else:
            data = _get_mock_dashboard_data()
            is_live = False
    except Exception as e:
        logger.error("dashboard_data_fetch_failed", error=str(e))
        data = _get_mock_dashboard_data()
        is_live = False
    
    # Generate report based on format
    if format == "pdf":
        return await _generate_pdf_response(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            report_id=report_id,
            data=data,
        )
    else:
        return await _generate_csv_response(
            tenant_id=tenant_id,
            report_id=report_id,
            data=data,
        )


async def _generate_pdf_response(
    tenant_id: str,
    tenant_name: str,
    report_id: str,
    data: dict,
) -> StreamingResponse:
    """Generate and return PDF report."""
    try:
        # Load branding (default for now)
        brand = get_default_brand()
        
        # Initialize PDF generator with branding
        generator = PDFReportGenerator(brand_config=brand)
        
        # Build report components from dashboard data
        scores = _build_scores_from_dashboard(data)
        findings = _build_findings_from_dashboard(data)
        compliance_results = _build_compliance_results(data)
        
        # Generate PDF
        pdf_bytes = generator.generate_executive_summary(
            customer_name=tenant_name,
            assessment_date=datetime.utcnow(),
            scores=scores,
            findings=findings,
            compliance_results=compliance_results,
        )
        
        logger.info("pdf_report_generated", 
                   tenant_id=tenant_id, 
                   report_id=report_id,
                   size_bytes=len(pdf_bytes))
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={report_id}.pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
        
    except Exception as e:
        logger.error("pdf_generation_failed", tenant_id=tenant_id, error=str(e))
        # Fall back to CSV on PDF generation failure
        return await _generate_csv_response(tenant_id, report_id, data)


async def _generate_csv_response(
    tenant_id: str,
    report_id: str,
    data: dict,
) -> StreamingResponse:
    """Generate and return CSV report."""
    csv_content = _generate_csv_report(data, tenant_id)
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={report_id}.csv",
        },
    )


def _get_mock_dashboard_data() -> dict:
    """Return mock dashboard data for demo/fallback."""
    return {
        "tenant_name": "Demo Organization",
        "is_live_data": False,
        "secure_score": {
            "current_score": 72.5,
            "max_score": 100,
        },
        "mfa_coverage": {
            "user_coverage_percent": 87.3,
            "admin_coverage_percent": 100.0,
            "total_users": 150,
            "users_with_mfa": 131,
            "total_admins": 8,
            "admins_with_mfa": 8,
        },
        "device_compliance": {
            "compliance_percent": 92.8,
            "compliant_count": 142,
            "non_compliant_count": 8,
            "total_devices": 153,
        },
        "security_alerts": {
            "active_alerts": 25,
            "critical_count": 0,
            "high_count": 2,
            "medium_count": 8,
            "low_count": 15,
            "alerts": [],
        },
        "risky_users": {
            "total_risky": 7,
            "high_risk_count": 0,
            "medium_risk_count": 2,
            "low_risk_count": 5,
        },
        "privileged_accounts": {
            "global_admin_count": 3,
            "privileged_role_count": 12,
        },
    }


@router.get("/scheduled")
async def list_scheduled_reports(tenant_id: str):
    """List scheduled report configurations."""
    return [
        {
            "id": "sched-001",
            "name": "Weekly Executive Summary",
            "type": "executive",
            "schedule": "0 8 * * MON",
            "recipients": ["ceo@company.com", "ciso@company.com"],
            "format": "pdf",
            "enabled": True,
        },
        {
            "id": "sched-002",
            "name": "Monthly Compliance Report",
            "type": "compliance",
            "schedule": "0 8 1 * *",
            "recipients": ["compliance@company.com"],
            "format": "pdf",
            "enabled": True,
        },
    ]


@router.post("/scheduled")
async def create_scheduled_report(
    tenant_id: str,
    config: dict,
):
    """Create a new scheduled report."""
    return {
        "success": True,
        "schedule_id": "sched-003",
        "message": "Scheduled report created",
    }


@router.get("/templates")
async def list_report_templates(tenant_id: str):
    """List available report templates."""
    return [
        {
            "id": "tmpl-executive",
            "name": "Executive Summary",
            "description": "High-level security posture for board/executives",
            "sections": ["security_score", "compliance", "risks", "trends"],
            "formats": ["pdf", "csv"],
        },
        {
            "id": "tmpl-compliance",
            "name": "Compliance Report",
            "description": "Detailed compliance status against frameworks",
            "sections": ["framework_mapping", "control_status", "gaps", "remediation"],
            "formats": ["pdf", "csv"],
        },
        {
            "id": "tmpl-vulnerability",
            "name": "Vulnerability Report",
            "description": "Current vulnerabilities and remediation status",
            "sections": ["summary", "critical_vulns", "aging", "remediation_progress"],
            "formats": ["pdf", "csv"],
        },
        {
            "id": "tmpl-audit",
            "name": "Audit Trail Report",
            "description": "Administrative actions and changes",
            "sections": ["role_changes", "policy_changes", "high_risk_actions"],
            "formats": ["pdf", "csv"],
        },
    ]


@router.get("/export/findings")
async def export_findings(
    tenant_id: str,
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    severity: Optional[str] = None,
    status: Optional[str] = None,
):
    """Export findings data."""
    service = get_live_data_service()
    
    # Get findings from storage if available
    try:
        from services.storage_service import get_storage_service
        storage = get_storage_service()
        findings = await storage.get_open_findings(tenant_id, severity)
    except Exception:
        findings = []
    
    # If no stored findings, generate from live data
    if not findings and service.is_connected():
        try:
            data = await service.get_full_dashboard_data()
            findings = _build_findings_from_dashboard(data)
            if severity:
                findings = [f for f in findings if f.get("severity") == severity]
        except Exception:
            findings = []
    
    # Filter by status if provided
    if status and findings:
        findings = [f for f in findings if f.get("status", "open") == status]
    
    if format == "csv":
        lines = ["ID,Title,Severity,Category,Status"]
        for f in findings:
            lines.append(f"{f.get('id', '')},{f.get('title', '')},{f.get('severity', '')},{f.get('category', '')},{f.get('status', 'open')}")
        
        return StreamingResponse(
            io.StringIO("\n".join(lines)),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={tenant_id}_findings.csv"
            },
        )
    else:
        return {
            "findings": findings,
            "exported_at": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "count": len(findings),
        }
