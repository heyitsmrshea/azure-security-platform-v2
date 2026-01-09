// Dashboard Types for Azure Security Platform V2

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'informational'
export type TrendDirection = 'up' | 'down' | 'stable'
export type BackupStatus = 'healthy' | 'warning' | 'critical' | 'unknown'

export interface MetricTrend {
  direction: TrendDirection
  change_value: number
  change_percent?: number
  period: string
}

export interface SecurityScore {
  current_score: number
  max_score: number
  percentile?: number
  trend?: MetricTrend
  comparison_label?: string
  last_updated: string
}

export interface ComplianceScore {
  framework: string
  score_percent: number
  controls_passed: number
  controls_total: number
  trend?: MetricTrend
  last_updated: string
}

export interface RiskSummary {
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  trend?: MetricTrend
  last_updated: string
}

export interface BackupHealth {
  protected_percent: number
  total_protected_items: number
  total_critical_systems: number
  last_successful_backup?: string
  hours_since_backup?: number
  status: BackupStatus
  last_updated: string
}

export interface RecoveryReadiness {
  rto_status: BackupStatus
  rpo_status: BackupStatus
  rto_target_hours: number
  rpo_target_hours: number
  rto_actual_hours?: number
  rpo_actual_hours?: number
  overall_status: BackupStatus
  last_updated: string
}

export interface MFACoverage {
  admin_coverage_percent: number
  user_coverage_percent: number
  total_admins: number
  admins_with_mfa: number
  total_users: number
  users_with_mfa: number
  trend?: MetricTrend
  last_updated: string
}

export interface PrivilegedAccounts {
  global_admin_count: number
  privileged_role_count: number
  pim_eligible_count: number
  pim_active_count: number
  trend?: MetricTrend
  last_updated: string
}

export interface RiskyUsers {
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  requires_investigation: number
  trend?: MetricTrend
  last_updated: string
}

export interface AlertSummary {
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  total_active: number
  last_updated: string
}

export interface BlockedThreats {
  phishing_blocked: number
  malware_blocked: number
  spam_blocked: number
  total_blocked: number
  period: string
  last_updated: string
}

export interface DeviceCompliance {
  compliant_count: number
  non_compliant_count: number
  unknown_count: number
  total_devices: number
  compliance_percent: number
  trend?: MetricTrend
  last_updated: string
}

export interface PatchSLACompliance {
  compliance_percent: number
  target_percent: number
  patches_in_sla: number
  patches_total: number
  critical_sla_days: number
  high_sla_days: number
  medium_sla_days: number
  last_updated: string
}

export interface FindingAgeDistribution {
  age_0_7: number
  age_7_30: number
  age_30_90: number
  age_90_plus: number
  total_open: number
  last_updated: string
}

export interface MTTR {
  mttr_days: number
  critical_mttr_days: number
  high_mttr_days: number
  findings_resolved_count: number
  period: string
  last_updated: string
}

export interface ScoreTrend {
  date: string
  secure_score: number
  compliance_score?: number
}

export interface TopRisk {
  title: string
  description: string
  severity: Severity
  affected_resources: number
  recommendation: string
}

export interface DataFreshness {
  last_updated: string
  minutes_ago: number
  status: 'fresh' | 'stale' | 'outdated'
}

export interface ExecutiveDashboard {
  tenant_id: string
  tenant_name: string
  security_score: SecurityScore
  compliance_score: ComplianceScore
  risk_summary: RiskSummary
  backup_health: BackupHealth
  recovery_readiness: RecoveryReadiness
  mfa_coverage: MFACoverage
  privileged_accounts: PrivilegedAccounts
  risky_users: RiskyUsers
  alert_summary: AlertSummary
  blocked_threats: BlockedThreats
  device_compliance: DeviceCompliance
  patch_sla: PatchSLACompliance
  finding_age: FindingAgeDistribution
  mttr: MTTR
  score_trend: ScoreTrend[]
  top_risks: TopRisk[]
  data_freshness: DataFreshness
}
