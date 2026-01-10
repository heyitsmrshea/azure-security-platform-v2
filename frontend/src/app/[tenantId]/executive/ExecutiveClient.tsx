'use client'

import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { MetricCard, ScoreCard } from '@/components/shared/MetricCard'
import { StatusBadge, SeverityBadge } from '@/components/shared/StatusBadge'
import { useState, useEffect, useCallback } from 'react'
import { RiskCard } from '@/components/executive/RiskCard'
import { TrendChart, FindingAgeChart } from '@/components/executive/TrendChart'
import { HealthGrade } from '@/components/executive/HealthGrade'
import { ExecutiveDashboard } from '@/types/dashboard'
import { cn } from '@/lib/utils'
import {
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
} from 'lucide-react'
import { AzureLinks } from '@/lib/azure-links'



export function ExecutiveClient({ tenantId }: { tenantId: string }) {
    const [data, setData] = useState<ExecutiveDashboard | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchData = useCallback(async () => {
        setIsLoading(true)
        setError(null)
        try {
            // Dynamically import apiClient to ensure it uses the correct env vars on client side
            const { apiClient } = await import('@/lib/api-client')
            const dashboardData = await apiClient.getExecutiveDashboard(tenantId)
            setData(dashboardData)
        } catch (err) {
            console.error('Failed to fetch executive dashboard:', err)
            setError('Failed to load dashboard data. Please try again.')
        } finally {
            setIsLoading(false)
        }
    }, [tenantId])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    if (isLoading) {
        return (
            <div className="min-h-screen bg-background-primary flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
                    <p className="text-foreground-muted">Loading dashboard...</p>
                </div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="min-h-screen bg-background-primary flex items-center justify-center">
                <div className="text-center space-y-4">
                    <p className="text-status-error">{error || 'No data available'}</p>
                    <button onClick={fetchData} className="btn-primary">Retry</button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background-primary">
            <DashboardHeader
                tenantName={data.tenant_name}
                tenantId={tenantId}
                title="Executive Dashboard"
                minutesAgo={data.data_freshness.minutes_ago}
                onRefresh={fetchData}
                isRefreshing={isLoading}
            />

            <main className="p-6 space-y-6">
                {/* Row 1: Primary Metrics */}
                <section>
                    <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
                        Security Posture
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {/* Health Grade - Large visual grade based on percentage */}
                        <div className="card flex items-center justify-center py-6">
                            <HealthGrade score={data.security_score.score_percent} />
                        </div>
                        <ScoreCard
                            label="Security Score"
                            score={data.security_score.score_percent}
                            maxScore={100}
                            trend={data.security_score.trend}
                            comparison={`${data.security_score.current_score.toFixed(0)}/${data.security_score.max_score.toFixed(0)} pts`}
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
                            actionLink={AzureLinks.incidents}
                            actionLabel="View Incidents"
                        />
                    </div>
                </section>

                {/* Industry Benchmarks - CEO view */}
                {data.security_score.benchmarks && (
                    <section>
                        <h2 className="text-sm font-medium text-foreground-muted uppercase tracking-wider mb-4">
                            Industry Benchmarks
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Your Score */}
                            <div className="card bg-gradient-to-br from-accent/5 to-transparent">
                                <div className="text-sm text-foreground-muted mb-2">Your Security Score</div>
                                <div className="text-4xl font-bold text-accent">
                                    {data.security_score.score_percent.toFixed(1)}%
                                </div>
                                <div className="text-xs text-foreground-muted mt-1">
                                    {data.security_score.current_score.toFixed(0)} / {data.security_score.max_score.toFixed(0)} points
                                </div>
                            </div>

                            {/* All Tenants Comparison */}
                            {data.security_score.benchmarks.all_tenants && (
                                <div className="card">
                                    <div className="text-sm text-foreground-muted mb-2">vs All Organizations</div>
                                    <div className="flex items-baseline gap-2">
                                        <span className={cn(
                                            'text-2xl font-bold',
                                            data.security_score.benchmarks.all_tenants.comparison === 'above' 
                                                ? 'text-status-success' 
                                                : 'text-status-error'
                                        )}>
                                            {data.security_score.benchmarks.all_tenants.difference > 0 ? '+' : ''}
                                            {data.security_score.benchmarks.all_tenants.difference.toFixed(1)}%
                                        </span>
                                        <span className="text-sm text-foreground-muted">
                                            {data.security_score.benchmarks.all_tenants.comparison === 'above' 
                                                ? 'above' 
                                                : 'below'} average
                                        </span>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-divider">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-foreground-muted">Global Average</span>
                                            <span className="text-foreground-secondary">
                                                {data.security_score.benchmarks.all_tenants.average_percent.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Similar Size Comparison */}
                            {data.security_score.benchmarks.similar_size && (
                                <div className="card">
                                    <div className="text-sm text-foreground-muted mb-2">
                                        vs Similar Size
                                        {data.security_score.benchmarks.similar_size.size_category && 
                                         data.security_score.benchmarks.similar_size.size_category !== 'Unknown' && (
                                            <span className="ml-1 text-xs">
                                                ({data.security_score.benchmarks.similar_size.size_category})
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-baseline gap-2">
                                        <span className={cn(
                                            'text-2xl font-bold',
                                            data.security_score.benchmarks.similar_size.comparison === 'above' 
                                                ? 'text-status-success' 
                                                : 'text-status-error'
                                        )}>
                                            {data.security_score.benchmarks.similar_size.difference > 0 ? '+' : ''}
                                            {data.security_score.benchmarks.similar_size.difference.toFixed(1)}%
                                        </span>
                                        <span className="text-sm text-foreground-muted">
                                            {data.security_score.benchmarks.similar_size.comparison === 'above' 
                                                ? 'above' 
                                                : 'below'} peers
                                        </span>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-divider">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-foreground-muted">Peer Average</span>
                                            <span className="text-foreground-secondary">
                                                {data.security_score.benchmarks.similar_size.average_percent.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Industry Comparison (if available) */}
                            {data.security_score.benchmarks.industry && (
                                <div className="card">
                                    <div className="text-sm text-foreground-muted mb-2">vs Industry</div>
                                    <div className="flex items-baseline gap-2">
                                        <span className={cn(
                                            'text-2xl font-bold',
                                            data.security_score.benchmarks.industry.comparison === 'above' 
                                                ? 'text-status-success' 
                                                : 'text-status-error'
                                        )}>
                                            {data.security_score.benchmarks.industry.difference > 0 ? '+' : ''}
                                            {data.security_score.benchmarks.industry.difference.toFixed(1)}%
                                        </span>
                                        <span className="text-sm text-foreground-muted">
                                            {data.security_score.benchmarks.industry.comparison === 'above' 
                                                ? 'above' 
                                                : 'below'} industry
                                        </span>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-divider">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-foreground-muted">Industry Average</span>
                                            <span className="text-foreground-secondary">
                                                {data.security_score.benchmarks.industry.average_percent.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* No industry data message */}
                            {!data.security_score.benchmarks.industry && (
                                <div className="card bg-background-secondary/50">
                                    <div className="text-sm text-foreground-muted mb-2">vs Industry</div>
                                    <div className="text-foreground-muted text-sm">
                                        Industry benchmark not available
                                    </div>
                                    <div className="text-xs text-foreground-muted mt-2">
                                        Set your industry in Microsoft 365 Admin Center to enable
                                    </div>
                                </div>
                            )}
                        </div>
                    </section>
                )}

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
                            isNotConfigured={data.backup_health.total_protected_items === 0}
                            actionLink={AzureLinks.backup}
                            actionLabel="Configure Backup"
                        />
                        <MetricCard
                            label="Last Successful Backup"
                            value={data.backup_health.hours_since_backup != null ? `${data.backup_health.hours_since_backup}h ago` : 'N/A'}
                            icon={<Clock className="w-5 h-5" />}
                            status={data.backup_health.hours_since_backup != null && data.backup_health.hours_since_backup <= 24 ? 'healthy' : 'warning'}
                            isNotConfigured={data.backup_health.total_protected_items === 0}
                            actionLink={AzureLinks.backup}
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
                            actionLink={AzureLinks.users}
                            actionLabel="Manage Users"
                        />
                        <MetricCard
                            label="Risky Users"
                            value={data.risky_users.requires_investigation}
                            icon={<UserX className="w-5 h-5" />}
                            trend={data.risky_users.trend}
                            status={data.risky_users.high_risk_count > 0 ? 'critical' : data.risky_users.requires_investigation > 0 ? 'warning' : 'healthy'}
                            comparison="Require investigation"
                            actionLink={AzureLinks.riskyUsers}
                            actionLabel="Investigate"
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
                            value={
                                // Show "N/A" if Defender data is not available (all zeros)
                                data.blocked_threats.total_blocked === 0 && 
                                data.blocked_threats.phishing_blocked === 0 && 
                                data.blocked_threats.malware_blocked === 0
                                    ? 'N/A'
                                    : data.blocked_threats.total_blocked
                            }
                            icon={<ShieldOff className="w-5 h-5" />}
                            status={data.blocked_threats.total_blocked > 0 ? 'healthy' : 'neutral'}
                            isNotConfigured={
                                data.blocked_threats.total_blocked === 0 && 
                                data.blocked_threats.phishing_blocked === 0 && 
                                data.blocked_threats.malware_blocked === 0
                            }
                            comparison={
                                data.blocked_threats.total_blocked > 0
                                    ? `${data.blocked_threats.phishing_blocked} phishing, ${data.blocked_threats.malware_blocked} malware`
                                    : 'Defender for O365 not configured'
                            }
                            actionLink={AzureLinks.securityCenter}
                            actionLabel={data.blocked_threats.total_blocked > 0 ? 'Defender' : 'Configure Defender'}
                        />
                        <MetricCard
                            label="Device Compliance"
                            value={
                                // Show "Unknown" if all devices are in unknown state
                                data.device_compliance.unknown_count === data.device_compliance.total_devices && data.device_compliance.total_devices > 0
                                    ? 'Unknown'
                                    : `${data.device_compliance.compliance_percent}%`
                            }
                            icon={<Laptop className="w-5 h-5" />}
                            trend={data.device_compliance.trend}
                            status={
                                // All devices unknown = neutral, otherwise use compliance percentage
                                data.device_compliance.unknown_count === data.device_compliance.total_devices
                                    ? 'neutral'
                                    : data.device_compliance.compliance_percent >= 90 ? 'healthy' : 'warning'
                            }
                            comparison={
                                // Show appropriate comparison based on state
                                data.device_compliance.unknown_count === data.device_compliance.total_devices
                                    ? `${data.device_compliance.total_devices} devices pending evaluation`
                                    : data.device_compliance.non_compliant_count > 0
                                        ? `${data.device_compliance.non_compliant_count} non-compliant`
                                        : `${data.device_compliance.total_devices} devices compliant`
                            }
                            actionLink={AzureLinks.devices}
                            actionLabel="Manage Devices"
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

