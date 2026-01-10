"""
Executive Dashboard API routes for Azure Security Platform V2

Provides all metrics for the executive dashboard including:
- Security Score
- Compliance Score
- Risk Summary
- Backup Health (Ransomware Readiness)
- Identity & Access metrics
- Threat Summary
- IT Accountability metrics
- Trends
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from models.schemas import (
    ExecutiveDashboard,
    SecurityScore,
    ComplianceScore,
    RiskSummary,
    BackupHealth,
    RecoveryReadiness,
    MFACoverage,
    PrivilegedAccounts,
    RiskyUsers,
    AlertSummary,
    BlockedThreats,
    DeviceCompliance,
    PatchSLACompliance,
    FindingAgeDistribution,
    MTTR,
    ScoreTrend,
    TopRisk,
    DataFreshness,
    MetricTrend,
    TrendDirection,
    BackupStatus,
    Severity,
    IndustryBenchmarks,
    BenchmarkComparison,
)
from services.live_data_service import get_live_data_service
from services.azure_client import get_azure_client
from services.storage_service import get_storage_service
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


async def _save_dashboard_snapshot(tenant_id: str, dashboard: ExecutiveDashboard):
    """
    Save dashboard snapshot for historical trending (fire-and-forget).
    """
    try:
        storage = get_storage_service()
        
        # Extract key metrics for trending
        snapshot_data = {
            "security_score": dashboard.security_score.current_score,
            "compliance_score": dashboard.compliance_score.score_percent,
            "mfa_coverage": dashboard.mfa_coverage.user_coverage_percent,
            "device_compliance": dashboard.device_compliance.compliance_percent,
            "critical_risks": dashboard.risk_summary.critical_count,
            "high_risks": dashboard.risk_summary.high_count,
            "total_alerts": dashboard.alert_summary.total_active,
            "global_admins": dashboard.privileged_accounts.global_admin_count,
            "risky_users": dashboard.risky_users.requires_investigation,
            "backup_health": dashboard.backup_health.protected_percent,
        }
        
        await storage.save_dashboard_snapshot(tenant_id, "executive", snapshot_data)
        
        # Also save security score separately for dedicated trend queries
        await storage.save_security_score(tenant_id, {
            "current_score": dashboard.security_score.current_score,
            "max_score": dashboard.security_score.max_score,
            "compliance_score": dashboard.compliance_score.score_percent,
        })
        
        logger.debug("dashboard_snapshot_saved", tenant_id=tenant_id)
    except Exception as e:
        # Don't fail the request if snapshot saving fails
        logger.warning("snapshot_save_failed", tenant_id=tenant_id, error=str(e))


# Tenant aliases for convenience (maps friendly names to actual tenant IDs)
TENANT_ALIASES = {
    "polaris": "cf47a479-9ed1-452d-896a-0e362307e969",
    "polaris-consulting": "cf47a479-9ed1-452d-896a-0e362307e969",
}

def resolve_tenant_id(tenant_id: str) -> str:
    """Resolve tenant aliases to actual tenant IDs."""
    return TENANT_ALIASES.get(tenant_id.lower(), tenant_id)

def is_real_tenant(tenant_id: str) -> bool:
    """Check if this is a real tenant (not demo) that should use live data."""
    demo_tenants = {"demo", "acme-corp", "globex", "initech"}
    resolved = resolve_tenant_id(tenant_id)
    return resolved.lower() not in demo_tenants


# ============================================================================
# LIVE DATA Endpoint - Uses real Azure data
# ============================================================================

@router.get("/live")
async def get_live_dashboard():
    """
    Get LIVE dashboard data from Azure tenant.
    
    This endpoint fetches real-time data from Microsoft Graph API
    using your configured service principal credentials.
    """
    service = get_live_data_service()
    
    if not service.is_connected():
        return {
            "error": "Not connected to Azure",
            "message": "Check AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables",
            "is_live": False,
        }
    
    data = await service.get_full_dashboard_data()
    return data


@router.get("/live/secure-score")
async def get_live_secure_score():
    """Get live Microsoft Secure Score."""
    service = get_live_data_service()
    return await service.get_secure_score()


@router.get("/live/mfa")
async def get_live_mfa_coverage():
    """Get live MFA coverage statistics."""
    service = get_live_data_service()
    return await service.get_mfa_coverage()


@router.get("/live/risky-users")
async def get_live_risky_users():
    """Get live risky users from Identity Protection."""
    service = get_live_data_service()
    return await service.get_risky_users()


@router.get("/live/privileged-accounts")
async def get_live_privileged_accounts():
    """Get live privileged account statistics."""
    service = get_live_data_service()
    return await service.get_privileged_accounts()


@router.get("/live/conditional-access")
async def get_live_conditional_access():
    """Get live Conditional Access policies."""
    service = get_live_data_service()
    return await service.get_conditional_access_policies()


@router.get("/live/devices")
async def get_live_device_compliance():
    """Get live device compliance from Intune."""
    service = get_live_data_service()
    return await service.get_device_compliance()


@router.get("/live/alerts")
async def get_live_security_alerts():
    """Get live security alerts."""
    service = get_live_data_service()
    return await service.get_security_alerts()


# ============================================================================
# Full Dashboard Endpoint - Live data for real tenants, mock for demo
# ============================================================================

@router.get("/dashboard", response_model=ExecutiveDashboard)
async def get_executive_dashboard(tenant_id: str):
    """
    Get complete executive dashboard data.
    
    Uses LIVE data for real tenant IDs, mock data for demo tenants.
    Supports tenant aliases like 'polaris' -> actual tenant ID.
    """
    # Resolve tenant aliases (e.g., 'polaris' -> actual UUID)
    resolved_tenant_id = resolve_tenant_id(tenant_id)
    
    now = datetime.utcnow()
    service = get_live_data_service()
    
    # Use live data for real tenant IDs (not demo tenants)
    use_live = is_real_tenant(resolved_tenant_id) and service.is_connected()
    
    if use_live:
        # Fetch live data from Azure
        live = await service.get_full_dashboard_data()
        mfa = live.get("mfa_coverage", {})
        priv = live.get("privileged_accounts", {})
        risky = live.get("risky_users", {})
        alerts = live.get("security_alerts", {})
        devices = live.get("device_compliance", {})
        
        # Get secure score data with actual max from API
        secure_score_data = live.get("secure_score", {})
        
        # Derive compliance from Secure Score controls
        # Count controls with score > 0 as "passed" (simplified compliance view)
        secure_controls = secure_score_data.get("controls", [])
        controls_total = len(secure_controls)
        controls_passed = len([c for c in secure_controls if c.get("score", 0) > 0])
        compliance_percent = round((controls_passed / controls_total * 100), 1) if controls_total > 0 else secure_score_data.get("score_percent", 0)
        
        # Build benchmark comparisons from Microsoft data
        benchmark_raw = secure_score_data.get("benchmarks", {})
        benchmarks = None
        comparison_label = f"{secure_score_data.get('score_percent', 0):.0f}% of max"
        
        if benchmark_raw:
            # Build IndustryBenchmarks model
            all_tenants = None
            similar_size = None
            industry = None
            
            if benchmark_raw.get("all_tenants"):
                at = benchmark_raw["all_tenants"]
                all_tenants = BenchmarkComparison(
                    average_score=at.get("average_score", 0),
                    average_percent=at.get("average_percent", 0),
                    comparison=at.get("comparison", "equal"),
                    difference=at.get("difference", 0),
                )
                # Update comparison label with benchmark context
                diff = at.get("difference", 0)
                if diff > 0:
                    comparison_label = f"+{diff:.0f}% vs average"
                elif diff < 0:
                    comparison_label = f"{diff:.0f}% vs average"
                else:
                    comparison_label = "At average"
            
            if benchmark_raw.get("similar_size"):
                ss = benchmark_raw["similar_size"]
                similar_size = BenchmarkComparison(
                    average_score=ss.get("average_score", 0),
                    average_percent=ss.get("average_percent", 0),
                    comparison=ss.get("comparison", "equal"),
                    difference=ss.get("difference", 0),
                    size_category=ss.get("size_category"),
                )
            
            if benchmark_raw.get("industry"):
                ind = benchmark_raw["industry"]
                industry = BenchmarkComparison(
                    average_score=ind.get("average_score", 0),
                    average_percent=ind.get("average_percent", 0),
                    comparison=ind.get("comparison", "equal"),
                    difference=ind.get("difference", 0),
                )
            
            benchmarks = IndustryBenchmarks(
                your_score_percent=benchmark_raw.get("your_score_percent", 0),
                all_tenants=all_tenants,
                similar_size=similar_size,
                industry=industry,
                organization_size=benchmark_raw.get("organization_size"),
            )
        
        dashboard = ExecutiveDashboard(
            tenant_id=resolved_tenant_id,
            tenant_name="Polaris Consulting LLC",
            security_score=SecurityScore(
                current_score=secure_score_data.get("current_score", 0),
                max_score=secure_score_data.get("max_score", 100),
                score_percent=secure_score_data.get("score_percent", 0),
                percentile=secure_score_data.get("percentile", 0),
                benchmarks=benchmarks,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                comparison_label=comparison_label, 
                last_updated=now,
            ),
            compliance_score=ComplianceScore(
                framework="Microsoft Secure Score",  # Honest about data source
                score_percent=compliance_percent,
                controls_passed=controls_passed,
                controls_total=controls_total,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            risk_summary=RiskSummary(
                critical_count=alerts.get("critical_count", 0), high_count=alerts.get("high_count", 0),
                medium_count=alerts.get("medium_count", 0), low_count=alerts.get("low_count", 0),
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            backup_health=BackupHealth(
                protected_percent=0, total_protected_items=0, total_critical_systems=0,
                last_successful_backup=None, hours_since_backup=None,
                status=BackupStatus.UNKNOWN, last_updated=now,
            ),
            recovery_readiness=RecoveryReadiness(
                rto_status=BackupStatus.UNKNOWN, rpo_status=BackupStatus.UNKNOWN,
                rto_target_hours=24, rpo_target_hours=4, rto_actual_hours=None, rpo_actual_hours=None,
                overall_status=BackupStatus.UNKNOWN, last_updated=now,
            ),
            mfa_coverage=MFACoverage(
                admin_coverage_percent=mfa.get("admin_coverage_percent", 0),
                user_coverage_percent=mfa.get("user_coverage_percent", 0),
                total_admins=mfa.get("total_admins", 0), admins_with_mfa=mfa.get("admins_with_mfa", 0),
                total_users=mfa.get("total_users", 0), users_with_mfa=mfa.get("users_with_mfa", 0),
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            privileged_accounts=PrivilegedAccounts(
                global_admin_count=priv.get("global_admin_count", 0),
                privileged_role_count=priv.get("privileged_role_count", 0),
                pim_eligible_count=0, pim_active_count=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            risky_users=RiskyUsers(
                high_risk_count=risky.get("high_risk_count", 0),
                medium_risk_count=risky.get("medium_risk_count", 0),
                low_risk_count=risky.get("low_risk_count", 0),
                requires_investigation=risky.get("high_risk_count", 0) + risky.get("medium_risk_count", 0),
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            alert_summary=AlertSummary(
                critical_count=alerts.get("critical_count", 0), high_count=alerts.get("high_count", 0),
                medium_count=alerts.get("medium_count", 0), low_count=alerts.get("low_count", 0),
                total_active=alerts.get("active_alerts", 0), last_updated=now,
            ),
            blocked_threats=BlockedThreats(
                phishing_blocked=0, malware_blocked=0, spam_blocked=0, total_blocked=0,
                period="30d", last_updated=now,
            ),
            device_compliance=DeviceCompliance(
                compliant_count=devices.get("compliant_count", 0),
                non_compliant_count=devices.get("non_compliant_count", 0),
                unknown_count=devices.get("unknown_count", 0),
                total_devices=devices.get("total_devices", 0),
                compliance_percent=devices.get("compliance_percent", 0),
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            ),
            patch_sla=PatchSLACompliance(
                compliance_percent=0, target_percent=95.0, patches_in_sla=0, patches_total=0,
                critical_sla_days=7, high_sla_days=14, medium_sla_days=30, last_updated=now,
            ),
            finding_age=FindingAgeDistribution(
                age_0_7=0, age_7_30=0, age_30_90=0, age_90_plus=0, total_open=0, last_updated=now,
            ),
            mttr=MTTR(
                mttr_days=0, critical_mttr_days=0, high_mttr_days=0, findings_resolved_count=0,
                period="30d", last_updated=now,
            ),
            score_trend=[ScoreTrend(date=now, secure_score=secure_score_data.get("score_percent", 0), compliance_score=compliance_percent)],
            top_risks=[
                TopRisk(
                    title="MFA Coverage Gap" if mfa.get("user_coverage_percent", 100) < 90 else "Review MFA",
                    description=f"{mfa.get('total_users', 0) - mfa.get('users_with_mfa', 0)} users without MFA",
                    severity=Severity.HIGH, affected_resources=mfa.get('total_users', 0) - mfa.get('users_with_mfa', 0),
                    recommendation="Enable MFA for all users",
                ),
                TopRisk(
                    title=f"{priv.get('global_admin_count', 0)} Global Admins",
                    description="Recommended: 2 or fewer Global Administrators",
                    severity=Severity.MEDIUM if priv.get('global_admin_count', 0) <= 5 else Severity.HIGH,
                    affected_resources=priv.get('global_admin_count', 0),
                    recommendation="Reduce Global Admins, use PIM",
                ),
            ],
            data_freshness=DataFreshness(last_updated=now, minutes_ago=0, status="live"),
        )
        
        # Save snapshot for historical trending (non-blocking)
        import asyncio
        asyncio.create_task(_save_dashboard_snapshot(tenant_id, dashboard))
        
        return dashboard
    
    # Demo/mock data for demo tenant IDs
    demo_dashboard = ExecutiveDashboard(
        tenant_id=tenant_id,
        tenant_name="Demo Tenant",
        
        # Row 1: Primary Metrics
        security_score=SecurityScore(
            current_score=72.5,
            max_score=100,
            score_percent=72.5,  # For demo, score equals percentage
            percentile=65,
            trend=MetricTrend(
                direction=TrendDirection.UP,
                change_value=3.2,
                change_percent=4.6,
                period="7d",
            ),
            comparison_label="Top 35%",
            last_updated=now,
        ),
        
        compliance_score=ComplianceScore(
            framework="CIS Azure 2.0",
            score_percent=68.5,
            controls_passed=137,
            controls_total=200,
            trend=MetricTrend(
                direction=TrendDirection.UP,
                change_value=2.1,
                change_percent=3.2,
                period="7d",
            ),
            last_updated=now,
        ),
        
        risk_summary=RiskSummary(
            critical_count=3,
            high_count=12,
            medium_count=45,
            low_count=89,
            trend=MetricTrend(
                direction=TrendDirection.DOWN,
                change_value=2,
                period="7d",
            ),
            last_updated=now,
        ),
        
        # Row 2: Ransomware Readiness
        backup_health=BackupHealth(
            protected_percent=94.5,
            total_protected_items=47,
            total_critical_systems=50,
            last_successful_backup=now - timedelta(hours=4),
            hours_since_backup=4,
            status=BackupStatus.HEALTHY,
            last_updated=now,
        ),
        
        recovery_readiness=RecoveryReadiness(
            rto_status=BackupStatus.HEALTHY,
            rpo_status=BackupStatus.HEALTHY,
            rto_target_hours=24,
            rpo_target_hours=4,
            rto_actual_hours=18,
            rpo_actual_hours=4,
            overall_status=BackupStatus.HEALTHY,
            last_updated=now,
        ),
        
        # Row 3: Identity & Access
        mfa_coverage=MFACoverage(
            admin_coverage_percent=100.0,
            user_coverage_percent=87.3,
            total_admins=8,
            admins_with_mfa=8,
            total_users=150,
            users_with_mfa=131,
            trend=MetricTrend(
                direction=TrendDirection.UP,
                change_value=2.5,
                period="7d",
            ),
            last_updated=now,
        ),
        
        privileged_accounts=PrivilegedAccounts(
            global_admin_count=3,
            privileged_role_count=12,
            pim_eligible_count=8,
            pim_active_count=2,
            trend=MetricTrend(
                direction=TrendDirection.STABLE,
                change_value=0,
                period="7d",
            ),
            last_updated=now,
        ),
        
        risky_users=RiskyUsers(
            high_risk_count=0,
            medium_risk_count=2,
            low_risk_count=5,
            requires_investigation=2,
            trend=MetricTrend(
                direction=TrendDirection.DOWN,
                change_value=1,
                period="7d",
            ),
            last_updated=now,
        ),
        
        # Row 4: Threat Summary
        alert_summary=AlertSummary(
            critical_count=0,
            high_count=2,
            medium_count=8,
            low_count=15,
            total_active=25,
            last_updated=now,
        ),
        
        blocked_threats=BlockedThreats(
            phishing_blocked=156,
            malware_blocked=23,
            spam_blocked=1247,
            total_blocked=1426,
            period="30d",
            last_updated=now,
        ),
        
        device_compliance=DeviceCompliance(
            compliant_count=142,
            non_compliant_count=8,
            unknown_count=3,
            total_devices=153,
            compliance_percent=92.8,
            trend=MetricTrend(
                direction=TrendDirection.UP,
                change_value=1.2,
                period="7d",
            ),
            last_updated=now,
        ),
        
        # Row 5: IT Accountability
        patch_sla=PatchSLACompliance(
            compliance_percent=89.5,
            target_percent=95.0,
            patches_in_sla=179,
            patches_total=200,
            critical_sla_days=7,
            high_sla_days=14,
            medium_sla_days=30,
            last_updated=now,
        ),
        
        finding_age=FindingAgeDistribution(
            age_0_7=15,
            age_7_30=28,
            age_30_90=12,
            age_90_plus=5,
            total_open=60,
            last_updated=now,
        ),
        
        mttr=MTTR(
            mttr_days=8.5,
            critical_mttr_days=2.1,
            high_mttr_days=5.3,
            findings_resolved_count=45,
            period="30d",
            last_updated=now,
        ),
        
        # Row 6: Progress & Trends
        score_trend=[
            ScoreTrend(date=now - timedelta(days=180), secure_score=58.2, compliance_score=52.1),
            ScoreTrend(date=now - timedelta(days=150), secure_score=61.5, compliance_score=55.8),
            ScoreTrend(date=now - timedelta(days=120), secure_score=64.8, compliance_score=59.2),
            ScoreTrend(date=now - timedelta(days=90), secure_score=67.2, compliance_score=62.5),
            ScoreTrend(date=now - timedelta(days=60), secure_score=69.5, compliance_score=65.1),
            ScoreTrend(date=now - timedelta(days=30), secure_score=71.2, compliance_score=67.3),
            ScoreTrend(date=now, secure_score=72.5, compliance_score=68.5),
        ],
        
        top_risks=[
            TopRisk(
                title="Legacy Authentication Enabled",
                description="3 applications still allow legacy authentication protocols that bypass MFA",
                severity=Severity.HIGH,
                affected_resources=3,
                recommendation="Disable legacy authentication in Conditional Access policies",
            ),
            TopRisk(
                title="Unpatched Critical Vulnerabilities",
                description="2 servers have critical vulnerabilities older than 7 days",
                severity=Severity.CRITICAL,
                affected_resources=2,
                recommendation="Apply security patches immediately",
            ),
            TopRisk(
                title="Excessive Global Admin Count",
                description="3 users have permanent Global Admin role (target: 2 or fewer)",
                severity=Severity.MEDIUM,
                affected_resources=3,
                recommendation="Convert to PIM eligible assignments",
            ),
            TopRisk(
                title="External Sharing Without Review",
                description="45 files shared externally haven't been reviewed in 90+ days",
                severity=Severity.MEDIUM,
                affected_resources=45,
                recommendation="Review and revoke unnecessary external shares",
            ),
            TopRisk(
                title="Stale Guest Accounts",
                description="12 guest accounts haven't signed in for 90+ days",
                severity=Severity.LOW,
                affected_resources=12,
                recommendation="Review and disable inactive guest accounts",
            ),
        ],
        
        data_freshness=DataFreshness(
            last_updated=now - timedelta(minutes=12),
            minutes_ago=12,
            status="fresh",
        ),
    )
    
    # Save demo snapshot for historical trending too (for demo purposes)
    import asyncio
    asyncio.create_task(_save_dashboard_snapshot(tenant_id, demo_dashboard))
    
    return demo_dashboard


# ============================================================================
# Individual Metric Endpoints
# ============================================================================

@router.get("/security-score", response_model=SecurityScore)
async def get_security_score(tenant_id: str):
    """Get current Microsoft Secure Score."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            data = await service.get_secure_score()
            if data.get("is_live"):
                return SecurityScore(
                    current_score=data.get("current_score", 0),
                    max_score=data.get("max_score", 100),
                    percentile=0, # Not available in standard endpoint
                    trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                    comparison_label="Live Data",
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_secure_score_fetch_failed", error=str(e), tenant_id=tenant_id)
            # Return zeroed struct on error for real tenant
            return SecurityScore(
                current_score=0, max_score=100, percentile=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                comparison_label="Error", last_updated=now
            )

    return SecurityScore(
        current_score=72.5,
        max_score=100,
        percentile=65,
        trend=MetricTrend(direction=TrendDirection.UP, change_value=3.2, period="7d"),
        comparison_label="Top 35%",
        last_updated=now,
    )


@router.get("/compliance-score", response_model=ComplianceScore)
async def get_compliance_score(
    tenant_id: str,
    framework: str = Query(default="CIS Azure 2.0"),
):
    """Get compliance score for specified framework."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        # Currently compliance is calculated on the fly in compliance.py but not exposed as score metric
        # We will return a placeholder "Calculating" state or 0
        return ComplianceScore(
            framework=framework,
            score_percent=0.0,
            controls_passed=0,
            controls_total=0,
            trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
            last_updated=now,
        )
        
    return ComplianceScore(
        framework=framework,
        score_percent=68.5,
        controls_passed=137,
        controls_total=200,
        trend=MetricTrend(direction=TrendDirection.UP, change_value=2.1, period="7d"),
        last_updated=now,
    )


@router.get("/risk-summary", response_model=RiskSummary)
async def get_risk_summary(tenant_id: str):
    """Get risk count by severity."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            alerts_data = await service.get_security_alerts()
            if alerts_data.get("is_live"):
                total_crit = 0
                total_high = 0
                total_med = 0
                total_low = 0
                
                for alert in alerts_data.get("alerts", []):
                    sev = str(alert.get("severity", "")).lower()
                    if "high" in sev: total_high += 1
                    elif "medium" in sev: total_med += 1
                    elif "low" in sev: total_low += 1
                    # Azure doesn't strictly have "critical" in standard mapping usually, mostly High/Med/Low
                    # but if it does:
                    elif "critical" in sev: total_crit += 1
                
                return RiskSummary(
                    critical_count=total_crit,
                    high_count=total_high,
                    medium_count=total_med,
                    low_count=total_low,
                    trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_risk_summary_fetch_failed", error=str(e), tenant_id=tenant_id)
            return RiskSummary(
                critical_count=0, high_count=0, medium_count=0, low_count=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now
            )
            
    return RiskSummary(
        critical_count=3,
        high_count=12,
        medium_count=45,
        low_count=89,
        trend=MetricTrend(direction=TrendDirection.DOWN, change_value=2, period="7d"),
        last_updated=now,
    )


@router.get("/backup-health", response_model=BackupHealth)
async def get_backup_health(tenant_id: str):
    """Get backup health metrics - RANSOMWARE READINESS."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return BackupHealth(
            protected_percent=0, total_protected_items=0, total_critical_systems=0,
            last_successful_backup=None, hours_since_backup=None,
            status=BackupStatus.UNKNOWN, last_updated=now,
        )

    return BackupHealth(
        protected_percent=94.5,
        total_protected_items=47,
        total_critical_systems=50,
        last_successful_backup=now - timedelta(hours=4),
        hours_since_backup=4,
        status=BackupStatus.HEALTHY,
        last_updated=now,
    )


@router.get("/recovery-readiness", response_model=RecoveryReadiness)
async def get_recovery_readiness(tenant_id: str):
    """Get RTO/RPO status - RANSOMWARE READINESS."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return RecoveryReadiness(
            rto_status=BackupStatus.UNKNOWN, rpo_status=BackupStatus.UNKNOWN,
            rto_target_hours=24, rpo_target_hours=4, rto_actual_hours=None, rpo_actual_hours=None,
            overall_status=BackupStatus.UNKNOWN, last_updated=now,
        )

    return RecoveryReadiness(
        rto_status=BackupStatus.HEALTHY,
        rpo_status=BackupStatus.HEALTHY,
        rto_target_hours=24,
        rpo_target_hours=4,
        rto_actual_hours=18,
        rpo_actual_hours=4,
        overall_status=BackupStatus.HEALTHY,
        last_updated=now,
    )


@router.get("/mfa-coverage", response_model=MFACoverage)
async def get_mfa_coverage(tenant_id: str):
    """Get MFA coverage metrics."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            mfa = await service.get_mfa_coverage()
            if mfa.get("is_live"):
                return MFACoverage(
                    admin_coverage_percent=mfa.get("admin_coverage_percent", 0),
                    user_coverage_percent=mfa.get("user_coverage_percent", 0),
                    total_admins=mfa.get("total_admins", 0), 
                    admins_with_mfa=mfa.get("admins_with_mfa", 0),
                    total_users=mfa.get("total_users", 0), 
                    users_with_mfa=mfa.get("users_with_mfa", 0),
                    trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_mfa_fetch_failed", error=str(e), tenant_id=tenant_id)
            return MFACoverage(
                admin_coverage_percent=0, user_coverage_percent=0,
                total_admins=0, admins_with_mfa=0, total_users=0, users_with_mfa=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now
            )
            
    return MFACoverage(
        admin_coverage_percent=100.0,
        user_coverage_percent=87.3,
        total_admins=8,
        admins_with_mfa=8,
        total_users=150,
        users_with_mfa=131,
        trend=MetricTrend(direction=TrendDirection.UP, change_value=2.5, period="7d"),
        last_updated=now,
    )


@router.get("/privileged-accounts", response_model=PrivilegedAccounts)
async def get_privileged_accounts(tenant_id: str):
    """Get privileged account metrics."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            data = await service.get_privileged_accounts()
            if data.get("is_live"):
                return PrivilegedAccounts(
                    global_admin_count=data.get("global_admin_count", 0),
                    privileged_role_count=data.get("privileged_role_count", 0),
                    pim_eligible_count=0, 
                    pim_active_count=0,
                    trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_privileged_accounts_fetch_failed", error=str(e), tenant_id=tenant_id)
            return PrivilegedAccounts(
                global_admin_count=0, privileged_role_count=0, pim_eligible_count=0, pim_active_count=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now
            )
            
    return PrivilegedAccounts(
        global_admin_count=3,
        privileged_role_count=12,
        pim_eligible_count=8,
        pim_active_count=2,
        trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
        last_updated=now,
    )


@router.get("/risky-users", response_model=RiskyUsers)
async def get_risky_users(tenant_id: str):
    """Get risky user count."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            risky = await service.get_risky_users() # Returns list of dicts
            # We need counts
            # live_data_service definition returns raw list from get_risky_users()
            # but usually get_full_dashboard_data aggregates it. 
            # Let's count manually.
            count_high = sum(1 for u in risky if str(u.get("risk_level")).lower() == "high")
            count_med = sum(1 for u in risky if str(u.get("risk_level")).lower() == "medium")
            count_low = sum(1 for u in risky if str(u.get("risk_level")).lower() == "low")
            
            return RiskyUsers(
                high_risk_count=count_high,
                medium_risk_count=count_med,
                low_risk_count=count_low,
                requires_investigation=count_high + count_med,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now,
            )
        except Exception as e:
            logger.error("live_risky_users_fetch_failed", error=str(e), tenant_id=tenant_id)
            return RiskyUsers(
                high_risk_count=0, medium_risk_count=0, low_risk_count=0, requires_investigation=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now
            )
            
    return RiskyUsers(
        high_risk_count=0,
        medium_risk_count=2,
        low_risk_count=5,
        requires_investigation=2,
        trend=MetricTrend(direction=TrendDirection.DOWN, change_value=1, period="7d"),
        last_updated=now,
    )


@router.get("/alerts", response_model=AlertSummary)
async def get_alert_summary(tenant_id: str):
    """Get active alerts by severity."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            alerts_data = await service.get_security_alerts()
            if alerts_data.get("is_live"):
                total_crit = 0
                total_high = 0
                total_med = 0
                total_low = 0
                
                for alert in alerts_data.get("alerts", []):
                    # Only count active/investigating alerts for summary
                    status = str(alert.get("status", "")).lower()
                    if status in ["resolved", "dismissed"]:
                        continue
                        
                    sev = str(alert.get("severity", "")).lower()
                    if "high" in sev: total_high += 1
                    elif "medium" in sev: total_med += 1
                    elif "low" in sev: total_low += 1
                    elif "critical" in sev: total_crit += 1
                
                return AlertSummary(
                    critical_count=total_crit,
                    high_count=total_high,
                    medium_count=total_med,
                    low_count=total_low,
                    total_active=total_crit + total_high + total_med + total_low,
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_alert_summary_fetch_failed", error=str(e), tenant_id=tenant_id)
            return AlertSummary(
                critical_count=0, high_count=0, medium_count=0, low_count=0, total_active=0,
                last_updated=now
            )
            
    return AlertSummary(
        critical_count=0,
        high_count=2,
        medium_count=8,
        low_count=15,
        total_active=25,
        last_updated=now,
    )


@router.get("/blocked-threats", response_model=BlockedThreats)
async def get_blocked_threats(tenant_id: str):
    """Get blocked threats this month."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return BlockedThreats(
            phishing_blocked=0, malware_blocked=0, spam_blocked=0, total_blocked=0,
            period="30d", last_updated=now,
        )

    return BlockedThreats(
        phishing_blocked=156,
        malware_blocked=23,
        spam_blocked=1247,
        total_blocked=1426,
        period="30d",
        last_updated=now,
    )


@router.get("/device-compliance", response_model=DeviceCompliance)
async def get_device_compliance(tenant_id: str):
    """Get device compliance metrics."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        try:
            service = get_live_data_service()
            data = await service.get_device_compliance()
            if data.get("is_live"):
                return DeviceCompliance(
                    compliant_count=data.get("compliant_count", 0),
                    non_compliant_count=data.get("non_compliant_count", 0),
                    unknown_count=data.get("unknown_count", 0),
                    total_devices=data.get("total_devices", 0),
                    compliance_percent=data.get("compliance_percent", 0),
                    trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                    last_updated=now,
                )
        except Exception as e:
            logger.error("live_device_compliance_fetch_failed", error=str(e), tenant_id=tenant_id)
            return DeviceCompliance(
                compliant_count=0, non_compliant_count=0, unknown_count=0, total_devices=0, compliance_percent=0,
                trend=MetricTrend(direction=TrendDirection.STABLE, change_value=0, period="7d"),
                last_updated=now
            )
    
    return DeviceCompliance(
        compliant_count=142,
        non_compliant_count=8,
        unknown_count=3,
        total_devices=153,
        compliance_percent=92.8,
        trend=MetricTrend(direction=TrendDirection.UP, change_value=1.2, period="7d"),
        last_updated=now,
    )


@router.get("/patch-sla", response_model=PatchSLACompliance)
async def get_patch_sla(tenant_id: str):
    """Get patch SLA compliance - IT ACCOUNTABILITY."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return PatchSLACompliance(
            compliance_percent=0, target_percent=95.0, patches_in_sla=0, patches_total=0,
            critical_sla_days=7, high_sla_days=14, medium_sla_days=30, last_updated=now,
        )

    return PatchSLACompliance(
        compliance_percent=89.5,
        target_percent=95.0,
        patches_in_sla=179,
        patches_total=200,
        critical_sla_days=7,
        high_sla_days=14,
        medium_sla_days=30,
        last_updated=now,
    )


@router.get("/finding-age", response_model=FindingAgeDistribution)
async def get_finding_age_distribution(tenant_id: str):
    """Get open finding age distribution - IT ACCOUNTABILITY."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return FindingAgeDistribution(
            age_0_7=0, age_7_30=0, age_30_90=0, age_90_plus=0, total_open=0, last_updated=now,
        )

    return FindingAgeDistribution(
        age_0_7=15,
        age_7_30=28,
        age_30_90=12,
        age_90_plus=5,
        total_open=60,
        last_updated=now,
    )


@router.get("/mttr", response_model=MTTR)
async def get_mttr(tenant_id: str):
    """Get Mean Time to Remediate - IT ACCOUNTABILITY."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return MTTR(
            mttr_days=0, critical_mttr_days=0, high_mttr_days=0, findings_resolved_count=0,
            period="30d", last_updated=now,
        )

    return MTTR(
        mttr_days=8.5,
        critical_mttr_days=2.1,
        high_mttr_days=5.3,
        findings_resolved_count=45,
        period="30d",
        last_updated=now,
    )


@router.get("/score-trend", response_model=list[ScoreTrend])
async def get_score_trend(
    tenant_id: str,
    days: int = Query(default=180, le=365),
):
    """Get historical score trend."""
    now = datetime.utcnow()
    
    if is_real_tenant(tenant_id):
        return [ScoreTrend(date=now, secure_score=0, compliance_score=0)]

    return [
        ScoreTrend(date=now - timedelta(days=180), secure_score=58.2, compliance_score=52.1),
        ScoreTrend(date=now - timedelta(days=150), secure_score=61.5, compliance_score=55.8),
        ScoreTrend(date=now - timedelta(days=120), secure_score=64.8, compliance_score=59.2),
        ScoreTrend(date=now - timedelta(days=90), secure_score=67.2, compliance_score=62.5),
        ScoreTrend(date=now - timedelta(days=60), secure_score=69.5, compliance_score=65.1),
        ScoreTrend(date=now - timedelta(days=30), secure_score=71.2, compliance_score=67.3),
        ScoreTrend(date=now, secure_score=72.5, compliance_score=68.5),
    ]


@router.get("/top-risks", response_model=list[TopRisk])
async def get_top_risks(tenant_id: str, limit: int = Query(default=5, le=10)):
    """Get top risks in plain English."""
    
    if is_real_tenant(tenant_id):
        # Dynamically generate risks from live status
        risks = []
        try:
            service = get_live_data_service()
            mfa = await service.get_mfa_coverage()
            priv = await service.get_privileged_accounts()
            
            # Risk 1: MFA Gaps
            if mfa.get("is_live"):
                users_total = mfa.get("total_users", 0)
                users_mfa = mfa.get("users_with_mfa", 0)
                if users_total > 0:
                    gap = users_total - users_mfa
                    percent = (users_mfa / users_total) * 100
                    if percent < 90:
                        risks.append(TopRisk(
                            title="MFA Coverage Gap",
                            description=f"{gap} users ({100-percent:.1f}%) do not have MFA registered.",
                            severity=Severity.HIGH,
                            affected_resources=gap,
                            recommendation="Enforce MFA registration for all users.",
                        ))
            
            # Risk 2: Global Admins
            if priv.get("is_live"):
                admins = priv.get("global_admin_count", 0)
                if admins > 5:
                    risks.append(TopRisk(
                        title="Excessive Global Admins",
                        description=f"{admins} accounts have Global Administrator privileges.",
                        severity=Severity.HIGH,
                        affected_resources=admins,
                        recommendation="Reduce to < 5 Global Admins and use PIM.",
                    ))
        except Exception:
            pass
            
        return risks[:limit]

    return [
        TopRisk(
            title="Legacy Authentication Enabled",
            description="3 applications still allow legacy authentication protocols that bypass MFA",
            severity=Severity.HIGH,
            affected_resources=3,
            recommendation="Disable legacy authentication in Conditional Access policies",
        ),
        TopRisk(
            title="Unpatched Critical Vulnerabilities",
            description="2 servers have critical vulnerabilities older than 7 days",
            severity=Severity.CRITICAL,
            affected_resources=2,
            recommendation="Apply security patches immediately",
        ),
    ][:limit]
