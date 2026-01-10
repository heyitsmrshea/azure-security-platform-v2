"""
Pydantic models for Azure Security Platform V2
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "informational"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class BackupStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    AT_RISK = "at_risk"
    NOT_CONFIGURED = "not_configured"
    UNKNOWN = "unknown"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


# ============================================================================
# Base Models
# ============================================================================

class TenantBase(BaseModel):
    id: str
    name: str
    azure_tenant_id: str
    is_active: bool = True


class TenantCreate(TenantBase):
    client_id: str
    client_secret: str  # Will be stored encrypted in Key Vault


class Tenant(TenantBase):
    created_at: datetime
    last_sync: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Executive Dashboard Models
# ============================================================================

class MetricTrend(BaseModel):
    """Trend information for a metric"""
    direction: TrendDirection
    change_value: float
    change_percent: Optional[float] = None
    period: str = "7d"


class BenchmarkComparison(BaseModel):
    """Comparison against a benchmark group"""
    average_score: float  # Raw score points
    average_percent: float  # Percentage
    comparison: str  # "above", "below", "equal"
    difference: float  # Percentage difference (positive = above average)
    size_category: Optional[str] = None  # For size-based benchmarks


class IndustryBenchmarks(BaseModel):
    """Microsoft Secure Score benchmark comparisons"""
    your_score_percent: float
    all_tenants: Optional[BenchmarkComparison] = None
    similar_size: Optional[BenchmarkComparison] = None
    industry: Optional[BenchmarkComparison] = None
    organization_size: Optional[int] = None  # Licensed user count


class SecurityScore(BaseModel):
    """Microsoft Secure Score metric - Note: Score is points-based, not percentage"""
    current_score: float = Field(..., ge=0)  # Actual score points (can exceed 100)
    max_score: float  # Maximum possible score points
    score_percent: float = Field(..., ge=0, le=100)  # Percentage: (current/max)*100
    percentile: Optional[int] = Field(None, ge=0, le=100)  # Comparison vs other tenants
    benchmarks: Optional[IndustryBenchmarks] = None  # Industry/size comparisons
    trend: Optional[MetricTrend] = None
    comparison_label: Optional[str] = None  # e.g., "Top 35%"
    last_updated: datetime


class ComplianceScore(BaseModel):
    """Framework compliance score"""
    framework: str  # e.g., "CIS Azure 2.0", "NIST 800-53"
    score_percent: float = Field(..., ge=0, le=100)
    controls_passed: int
    controls_total: int
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class RiskSummary(BaseModel):
    """Risk count by severity"""
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class BackupHealth(BaseModel):
    """Backup health metrics - POST-RANSOMWARE PRIORITY"""
    protected_percent: float = Field(..., ge=0, le=100)
    total_protected_items: int
    total_critical_systems: int
    last_successful_backup: Optional[datetime] = None
    hours_since_backup: Optional[int] = None
    status: BackupStatus
    last_updated: datetime


class RecoveryReadiness(BaseModel):
    """RTO/RPO status indicator"""
    rto_status: BackupStatus  # Recovery Time Objective
    rpo_status: BackupStatus  # Recovery Point Objective
    rto_target_hours: int
    rpo_target_hours: int
    rto_actual_hours: Optional[int] = None
    rpo_actual_hours: Optional[int] = None
    overall_status: BackupStatus
    last_updated: datetime


class MFACoverage(BaseModel):
    """MFA coverage metrics"""
    admin_coverage_percent: float = Field(..., ge=0, le=100)
    user_coverage_percent: float = Field(..., ge=0, le=100)
    total_admins: int
    admins_with_mfa: int
    total_users: int
    users_with_mfa: int
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class PrivilegedAccounts(BaseModel):
    """Privileged account metrics"""
    global_admin_count: int
    privileged_role_count: int  # All privileged roles
    pim_eligible_count: int
    pim_active_count: int
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class RiskyUsers(BaseModel):
    """Risky user count"""
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    requires_investigation: int
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class AlertSummary(BaseModel):
    """Active alerts by severity"""
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    total_active: int = 0
    last_updated: datetime


class BlockedThreats(BaseModel):
    """Blocked threats this month"""
    phishing_blocked: int
    malware_blocked: int
    spam_blocked: int
    total_blocked: int
    period: str = "30d"
    last_updated: datetime


class DeviceCompliance(BaseModel):
    """Device compliance metrics"""
    compliant_count: int
    non_compliant_count: int
    unknown_count: int
    total_devices: int
    compliance_percent: float = Field(..., ge=0, le=100)
    trend: Optional[MetricTrend] = None
    last_updated: datetime


class PatchSLACompliance(BaseModel):
    """Patch SLA compliance - IT Accountability"""
    compliance_percent: float = Field(..., ge=0, le=100)
    target_percent: float = Field(default=95.0, ge=0, le=100)
    patches_in_sla: int
    patches_total: int
    critical_sla_days: int = 7
    high_sla_days: int = 14
    medium_sla_days: int = 30
    last_updated: datetime


class FindingAgeDistribution(BaseModel):
    """Open finding age distribution - IT Accountability"""
    age_0_7: int = 0
    age_7_30: int = 0
    age_30_90: int = 0
    age_90_plus: int = 0
    total_open: int = 0
    last_updated: datetime


class MTTR(BaseModel):
    """Mean Time to Remediate - IT Accountability"""
    mttr_days: float
    critical_mttr_days: float
    high_mttr_days: float
    findings_resolved_count: int
    period: str = "30d"
    last_updated: datetime


class ScoreTrend(BaseModel):
    """Historical score trend data point"""
    date: datetime
    secure_score: float
    compliance_score: Optional[float] = None


class TopRisk(BaseModel):
    """Plain English risk description"""
    title: str
    description: str
    severity: Severity
    affected_resources: int
    recommendation: str


class DataFreshness(BaseModel):
    """Data freshness indicator"""
    last_updated: datetime
    minutes_ago: int
    status: str  # "fresh", "stale", "outdated"


# ============================================================================
# Executive Dashboard Aggregate
# ============================================================================

class ExecutiveDashboard(BaseModel):
    """Complete executive dashboard data"""
    tenant_id: str
    tenant_name: str
    
    # Row 1: Primary Metrics
    security_score: SecurityScore
    compliance_score: ComplianceScore
    risk_summary: RiskSummary
    
    # Row 2: Ransomware Readiness
    backup_health: BackupHealth
    recovery_readiness: RecoveryReadiness
    
    # Row 3: Identity & Access
    mfa_coverage: MFACoverage
    privileged_accounts: PrivilegedAccounts
    risky_users: RiskyUsers
    
    # Row 4: Threat Summary
    alert_summary: AlertSummary
    blocked_threats: BlockedThreats
    device_compliance: DeviceCompliance
    
    # Row 5: IT Accountability
    patch_sla: PatchSLACompliance
    finding_age: FindingAgeDistribution
    mttr: MTTR
    
    # Row 6: Progress & Trends
    score_trend: list[ScoreTrend]
    top_risks: list[TopRisk]
    data_freshness: DataFreshness


# ============================================================================
# IT Staff Dashboard Models
# ============================================================================

class SecurityAlert(BaseModel):
    """Security alert detail"""
    id: str
    title: str
    description: str
    severity: Severity
    status: str
    category: str
    resource_name: str
    resource_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class Vulnerability(BaseModel):
    """Vulnerability detail"""
    id: str
    cve_id: Optional[str] = None
    title: str
    description: str
    severity: Severity
    cvss_score: Optional[float] = None
    affected_resource: str
    resource_type: str
    first_seen: datetime
    status: str
    remediation: Optional[str] = None


class MFAGap(BaseModel):
    """User without MFA"""
    user_id: str
    display_name: str
    email: str
    department: Optional[str] = None
    is_admin: bool
    last_sign_in: Optional[datetime] = None


class ConditionalAccessPolicy(BaseModel):
    """Conditional Access policy"""
    id: str
    name: str
    state: str  # enabled, disabled, enabledForReportingButNotEnforced
    grant_controls: list[str]
    conditions: dict
    created_at: datetime
    modified_at: Optional[datetime] = None


class PrivilegedUser(BaseModel):
    """Privileged user detail"""
    user_id: str
    display_name: str
    email: str
    roles: list[str]
    is_pim_eligible: bool
    is_pim_active: bool
    last_activity: Optional[datetime] = None
    mfa_enabled: bool


class RiskySignIn(BaseModel):
    """Risky sign-in event"""
    id: str
    user_id: str
    display_name: str
    email: str
    risk_level: str
    risk_detail: str
    location: str
    ip_address: str
    app_display_name: str
    sign_in_time: datetime


class NonCompliantDevice(BaseModel):
    """Non-compliant device"""
    device_id: str
    device_name: str
    os_type: str
    os_version: str
    owner: str
    compliance_state: str
    failure_reasons: list[str]
    last_check_in: datetime


class GuestUser(BaseModel):
    """Guest/external user"""
    user_id: str
    display_name: str
    email: str
    source: str  # e.g., "Invited", "B2B"
    created_at: datetime
    last_sign_in: Optional[datetime] = None
    access_level: str


class ThirdPartyApp(BaseModel):
    """Third-party app with permissions"""
    app_id: str
    display_name: str
    publisher: str
    permissions: list[str]
    consent_type: str  # admin, user
    consented_by: str
    consented_at: datetime


class BackupJob(BaseModel):
    """Backup job status"""
    job_id: str
    protected_item: str
    vault_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    error_message: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: str
    activity: str
    category: str
    initiated_by: str
    target_resource: str
    result: str
    timestamp: datetime
    details: Optional[dict] = None


# ============================================================================
# API Response Models
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list
    total: int
    page: int
    page_size: int
    has_more: bool
