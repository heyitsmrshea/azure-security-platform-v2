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

from ...models.schemas import (
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
)

router = APIRouter()


# ============================================================================
# Full Dashboard Endpoint
# ============================================================================

@router.get("/dashboard", response_model=ExecutiveDashboard)
async def get_executive_dashboard(tenant_id: str):
    """
    Get complete executive dashboard data.
    
    Returns all metrics in a single response for efficient loading.
    """
    now = datetime.utcnow()
    
    # In production, this would fetch from collectors/cache
    # For now, return structured mock data
    
    return ExecutiveDashboard(
        tenant_id=tenant_id,
        tenant_name="Demo Tenant",
        
        # Row 1: Primary Metrics
        security_score=SecurityScore(
            current_score=72.5,
            max_score=100,
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


# ============================================================================
# Individual Metric Endpoints
# ============================================================================

@router.get("/security-score", response_model=SecurityScore)
async def get_security_score(tenant_id: str):
    """Get current Microsoft Secure Score."""
    now = datetime.utcnow()
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
