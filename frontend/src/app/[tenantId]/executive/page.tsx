'use client'

import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { MetricCard, ScoreCard } from '@/components/shared/MetricCard'
import { StatusBadge, SeverityBadge } from '@/components/shared/StatusBadge'
import { RiskCard } from '@/components/executive/RiskCard'
import { TrendChart, FindingAgeChart } from '@/components/executive/TrendChart'
import { ExecutiveDashboard } from '@/types/dashboard'
import { 
  Shield, 
  ShieldCheck,
  AlertTriangle,
  HardDrive,
  Clock,
  Users,
  UserCog,
  UserX,
  Bell,
  ShieldOff,
  Laptop,
  Timer,
  ListChecks,
  Gauge
} from 'lucide-react'

// Mock data - in production this would come from the API
const mockDashboard: ExecutiveDashboard = {
  tenant_id: 'demo',
  tenant_name: 'Demo Organization',
  security_score: {
    current_score: 72.5,
    max_score: 100,
    percentile: 65,
    trend: { direction: 'up', change_value: 3.2, change_percent: 4.6, period: '7d' },
    comparison_label: 'Top 35%',
    last_updated: new Date().toISOString(),
  },
  compliance_score: {
    framework: 'CIS Azure 2.0',
    score_percent: 68.5,
    controls_passed: 137,
    controls_total: 200,
    trend: { direction: 'up', change_value: 2.1, change_percent: 3.2, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  risk_summary: {
    critical_count: 3,
    high_count: 12,
    medium_count: 45,
    low_count: 89,
    trend: { direction: 'down', change_value: 2, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  backup_health: {
    protected_percent: 94.5,
    total_protected_items: 47,
    total_critical_systems: 50,
    last_successful_backup: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    hours_since_backup: 4,
    status: 'healthy',
    last_updated: new Date().toISOString(),
  },
  recovery_readiness: {
    rto_status: 'healthy',
    rpo_status: 'healthy',
    rto_target_hours: 24,
    rpo_target_hours: 4,
    rto_actual_hours: 18,
    rpo_actual_hours: 4,
    overall_status: 'healthy',
    last_updated: new Date().toISOString(),
  },
  mfa_coverage: {
    admin_coverage_percent: 100,
    user_coverage_percent: 87.3,
    total_admins: 8,
    admins_with_mfa: 8,
    total_users: 150,
    users_with_mfa: 131,
    trend: { direction: 'up', change_value: 2.5, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  privileged_accounts: {
    global_admin_count: 3,
    privileged_role_count: 12,
    pim_eligible_count: 8,
    pim_active_count: 2,
    trend: { direction: 'stable', change_value: 0, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  risky_users: {
    high_risk_count: 0,
    medium_risk_count: 2,
    low_risk_count: 5,
    requires_investigation: 2,
    trend: { direction: 'down', change_value: 1, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  alert_summary: {
    critical_count: 0,
    high_count: 2,
    medium_count: 8,
    low_count: 15,
    total_active: 25,
    last_updated: new Date().toISOString(),
  },
  blocked_threats: {
    phishing_blocked: 156,
    malware_blocked: 23,
    spam_blocked: 1247,
    total_blocked: 1426,
    period: '30d',
    last_updated: new Date().toISOString(),
  },
  device_compliance: {
    compliant_count: 142,
    non_compliant_count: 8,
    unknown_count: 3,
    total_devices: 153,
    compliance_percent: 92.8,
    trend: { direction: 'up', change_value: 1.2, period: '7d' },
    last_updated: new Date().toISOString(),
  },
  patch_sla: {
    compliance_percent: 89.5,
    target_percent: 95,
    patches_in_sla: 179,
    patches_total: 200,
    critical_sla_days: 7,
    high_sla_days: 14,
    medium_sla_days: 30,
    last_updated: new Date().toISOString(),
  },
  finding_age: {
    age_0_7: 15,
    age_7_30: 28,
    age_30_90: 12,
    age_90_plus: 5,
    total_open: 60,
    last_updated: new Date().toISOString(),
  },
  mttr: {
    mttr_days: 8.5,
    critical_mttr_days: 2.1,
    high_mttr_days: 5.3,
    findings_resolved_count: 45,
    period: '30d',
    last_updated: new Date().toISOString(),
  },
  score_trend: [
    { date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 58.2, compliance_score: 52.1 },
    { date: new Date(Date.now() - 150 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 61.5, compliance_score: 55.8 },
    { date: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 64.8, compliance_score: 59.2 },
    { date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 67.2, compliance_score: 62.5 },
    { date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 69.5, compliance_score: 65.1 },
    { date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 71.2, compliance_score: 67.3 },
    { date: new Date().toISOString(), secure_score: 72.5, compliance_score: 68.5 },
  ],
  top_risks: [
    {
      title: 'Legacy Authentication Enabled',
      description: '3 applications still allow legacy authentication protocols that bypass MFA',
      severity: 'high',
      affected_resources: 3,
      recommendation: 'Disable legacy authentication in Conditional Access policies',
    },
    {
      title: 'Unpatched Critical Vulnerabilities',
      description: '2 servers have critical vulnerabilities older than 7 days',
      severity: 'critical',
      affected_resources: 2,
      recommendation: 'Apply security patches immediately',
    },
    {
      title: 'Excessive Global Admin Count',
      description: '3 users have permanent Global Admin role (target: 2 or fewer)',
      severity: 'medium',
      affected_resources: 3,
      recommendation: 'Convert to PIM eligible assignments',
    },
    {
      title: 'External Sharing Without Review',
      description: "45 files shared externally haven't been reviewed in 90+ days",
      severity: 'medium',
      affected_resources: 45,
      recommendation: 'Review and revoke unnecessary external shares',
    },
    {
      title: 'Stale Guest Accounts',
      description: "12 guest accounts haven't signed in for 90+ days",
      severity: 'low',
      affected_resources: 12,
      recommendation: 'Review and disable inactive guest accounts',
    },
  ],
  data_freshness: {
    last_updated: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
    minutes_ago: 12,
    status: 'fresh',
  },
}

export default function ExecutiveDashboardPage({
  params,
}: {
  params: { tenantId: string }
}) {
  const data = mockDashboard

  return (
    <div className="min-h-screen bg-background-primary">
      <DashboardHeader
        tenantName={data.tenant_name}
        title="Executive Dashboard"
        minutesAgo={data.data_freshness.minutes_ago}
        onRefresh={() => console.log('Refresh')}
      />

      <main className="p-6 space-y-6">
        {/* Row 1: Primary Metrics */}
        <section>
          <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
            Security Posture
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ScoreCard
              label="Security Score"
              score={data.security_score.current_score}
              maxScore={data.security_score.max_score}
              trend={data.security_score.trend}
              comparison={data.security_score.comparison_label}
            />
            <ScoreCard
              label="Compliance Score"
              score={data.compliance_score.score_percent}
              trend={data.compliance_score.trend}
              comparison={`${data.compliance_score.controls_passed}/${data.compliance_score.controls_total} controls`}
            />
            <MetricCard
              label="Active Risks"
              value={data.risk_summary.critical_count + data.risk_summary.high_count}
              trend={data.risk_summary.trend}
              icon={<AlertTriangle className="w-5 h-5" />}
              status={data.risk_summary.critical_count > 0 ? 'critical' : data.risk_summary.high_count > 5 ? 'warning' : 'healthy'}
              comparison={`${data.risk_summary.critical_count} Critical, ${data.risk_summary.high_count} High`}
            />
          </div>
        </section>

        {/* Row 2: Ransomware Readiness */}
        <section>
          <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
            Ransomware Readiness
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              label="Backup Health"
              value={`${data.backup_health.protected_percent}%`}
              icon={<HardDrive className="w-5 h-5" />}
              status={data.backup_health.status === 'healthy' ? 'healthy' : data.backup_health.status === 'warning' ? 'warning' : 'critical'}
              comparison={`${data.backup_health.total_protected_items}/${data.backup_health.total_critical_systems} systems protected`}
            />
            <MetricCard
              label="Last Successful Backup"
              value={`${data.backup_health.hours_since_backup}h ago`}
              icon={<Clock className="w-5 h-5" />}
              status={data.backup_health.hours_since_backup && data.backup_health.hours_since_backup <= 24 ? 'healthy' : 'warning'}
            />
            <div className="card">
              <div className="kpi-label mb-3">Recovery Readiness</div>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-foreground-secondary">RTO</span>
                    <StatusBadge status={data.recovery_readiness.rto_status} size="sm" />
                  </div>
                  <div className="text-sm text-foreground-muted">
                    {data.recovery_readiness.rto_actual_hours}h / {data.recovery_readiness.rto_target_hours}h target
                  </div>
                </div>
                <div className="w-px h-12 bg-divider" />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-foreground-secondary">RPO</span>
                    <StatusBadge status={data.recovery_readiness.rpo_status} size="sm" />
                  </div>
                  <div className="text-sm text-foreground-muted">
                    {data.recovery_readiness.rpo_actual_hours}h / {data.recovery_readiness.rpo_target_hours}h target
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Row 3: Identity & Access */}
        <section>
          <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
            Identity & Access
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <span className="kpi-label">MFA Coverage</span>
                <Users className="w-5 h-5 text-foreground-muted" />
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-foreground-secondary">Admins</span>
                    <span className="font-medium text-status-success">{data.mfa_coverage.admin_coverage_percent}%</span>
                  </div>
                  <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-status-success rounded-full" 
                      style={{ width: `${data.mfa_coverage.admin_coverage_percent}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-foreground-secondary">All Users</span>
                    <span className="font-medium text-foreground-primary">{data.mfa_coverage.user_coverage_percent}%</span>
                  </div>
                  <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-accent rounded-full" 
                      style={{ width: `${data.mfa_coverage.user_coverage_percent}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
            <MetricCard
              label="Global Admins"
              value={data.privileged_accounts.global_admin_count}
              icon={<UserCog className="w-5 h-5" />}
              status={data.privileged_accounts.global_admin_count > 3 ? 'warning' : 'healthy'}
              comparison={`${data.privileged_accounts.pim_eligible_count} PIM eligible`}
            />
            <MetricCard
              label="Risky Users"
              value={data.risky_users.requires_investigation}
              icon={<UserX className="w-5 h-5" />}
              trend={data.risky_users.trend}
              status={data.risky_users.high_risk_count > 0 ? 'critical' : data.risky_users.requires_investigation > 0 ? 'warning' : 'healthy'}
              comparison="Require investigation"
            />
          </div>
        </section>

        {/* Row 4: Threat Summary */}
        <section>
          <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
            Threat Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <span className="kpi-label">Active Alerts</span>
                <Bell className="w-5 h-5 text-foreground-muted" />
              </div>
              <div className="text-3xl font-bold text-foreground-primary mb-3">
                {data.alert_summary.total_active}
              </div>
              <div className="flex flex-wrap gap-2">
                {data.alert_summary.critical_count > 0 && (
                  <SeverityBadge severity="critical" count={data.alert_summary.critical_count} size="sm" />
                )}
                {data.alert_summary.high_count > 0 && (
                  <SeverityBadge severity="high" count={data.alert_summary.high_count} size="sm" />
                )}
                {data.alert_summary.medium_count > 0 && (
                  <SeverityBadge severity="medium" count={data.alert_summary.medium_count} size="sm" />
                )}
              </div>
            </div>
            <MetricCard
              label="Threats Blocked (30d)"
              value={data.blocked_threats.total_blocked}
              icon={<ShieldOff className="w-5 h-5" />}
              status="healthy"
              comparison={`${data.blocked_threats.phishing_blocked} phishing, ${data.blocked_threats.malware_blocked} malware`}
            />
            <MetricCard
              label="Device Compliance"
              value={`${data.device_compliance.compliance_percent}%`}
              icon={<Laptop className="w-5 h-5" />}
              trend={data.device_compliance.trend}
              status={data.device_compliance.compliance_percent >= 90 ? 'healthy' : 'warning'}
              comparison={`${data.device_compliance.non_compliant_count} non-compliant`}
            />
          </div>
        </section>

        {/* Row 5: IT Accountability */}
        <section>
          <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
            IT Accountability
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <span className="kpi-label">Patch SLA Compliance</span>
                <ListChecks className="w-5 h-5 text-foreground-muted" />
              </div>
              <div className="flex items-end gap-2 mb-2">
                <span className="text-3xl font-bold text-foreground-primary">
                  {data.patch_sla.compliance_percent}%
                </span>
                <span className="text-sm text-foreground-muted mb-1">
                  / {data.patch_sla.target_percent}% target
                </span>
              </div>
              <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${data.patch_sla.compliance_percent >= data.patch_sla.target_percent ? 'bg-status-success' : 'bg-status-warning'}`}
                  style={{ width: `${data.patch_sla.compliance_percent}%` }}
                />
              </div>
            </div>
            <FindingAgeChart data={data.finding_age} />
            <MetricCard
              label="MTTR"
              value={`${data.mttr.mttr_days} days`}
              icon={<Timer className="w-5 h-5" />}
              status={data.mttr.mttr_days <= 7 ? 'healthy' : data.mttr.mttr_days <= 14 ? 'warning' : 'critical'}
              comparison={`Critical: ${data.mttr.critical_mttr_days}d, High: ${data.mttr.high_mttr_days}d`}
            />
          </div>
        </section>

        {/* Row 6: Trends and Risks */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <TrendChart data={data.score_trend} />
          <RiskCard risks={data.top_risks} />
        </section>
      </main>
    </div>
  )
}
