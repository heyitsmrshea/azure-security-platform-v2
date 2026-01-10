'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import {
    Building2,
    AlertTriangle,
    ExternalLink,
    RefreshCw,
    Download
} from 'lucide-react'
import { TenantRankingTable } from '@/components/msp/TenantRankingTable'
import { HealthGradeBadge } from '@/components/executive/HealthGrade'

// Mock data - in production this would come from /api/msp/overview
const mockOverview = {
    total_tenants: 5,
    healthy_tenants: 2,
    warning_tenants: 2,
    critical_tenants: 1,
    average_security_score: 74.8,
    average_compliance_score: 70.5,
    total_critical_risks: 13,
    total_high_risks: 56,
    total_active_alerts: 30,
    tenants: [
        { tenant_id: 'globex', tenant_name: 'Globex Industries', security_score: 58.1, compliance_score: 52.3, critical_risks: 8, high_risks: 22, mfa_coverage_percent: 62.1, device_compliance_percent: 71.5, backup_health_percent: 78.0, active_alerts: 15, status: 'critical' },
        { tenant_id: 'umbrella', tenant_name: 'Umbrella Corp', security_score: 67.3, compliance_score: 61.2, critical_risks: 2, high_risks: 15, mfa_coverage_percent: 78.5, device_compliance_percent: 85.2, backup_health_percent: 88.0, active_alerts: 8, status: 'warning' },
        { tenant_id: 'demo', tenant_name: 'Demo Organization', security_score: 72.5, compliance_score: 68.5, critical_risks: 3, high_risks: 12, mfa_coverage_percent: 87.3, device_compliance_percent: 92.8, backup_health_percent: 94.5, active_alerts: 5, status: 'warning' },
        { tenant_id: 'acme-corp', tenant_name: 'Acme Corporation', security_score: 85.2, compliance_score: 82.1, critical_risks: 0, high_risks: 5, mfa_coverage_percent: 98.5, device_compliance_percent: 95.3, backup_health_percent: 100.0, active_alerts: 2, status: 'healthy' },
        { tenant_id: 'initech', tenant_name: 'Initech Solutions', security_score: 91.0, compliance_score: 88.5, critical_risks: 0, high_risks: 2, mfa_coverage_percent: 100.0, device_compliance_percent: 98.1, backup_health_percent: 100.0, active_alerts: 0, status: 'healthy' },
    ],
}

const crossTenantAlerts = [
    { id: 'xta-001', title: 'Legacy Authentication Still Enabled', severity: 'high', tenant_count: 3 },
    { id: 'xta-002', title: 'Critical Patches Overdue', severity: 'critical', tenant_count: 1 },
    { id: 'xta-003', title: 'MFA Coverage Below 80%', severity: 'high', tenant_count: 2 },
]

export default function MSPOverviewPage() {
    const [isRefreshing, setIsRefreshing] = useState(false)
    const data = mockOverview

    const handleRefresh = async () => {
        setIsRefreshing(true)
        await new Promise(resolve => setTimeout(resolve, 1000))
        setIsRefreshing(false)
    }

    return (
        <div className="min-h-screen bg-background-primary">
            {/* Header */}
            <header className="border-b border-divider bg-background-secondary">
                <div className="px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                                <Building2 className="w-7 h-7 text-accent" />
                            </div>
                            <div>
                                <h1 className="text-xl font-semibold text-foreground-primary">
                                    MSP Dashboard
                                </h1>
                                <p className="text-sm text-foreground-muted">
                                    Managing {data.total_tenants} tenants
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <button
                                onClick={handleRefresh}
                                disabled={isRefreshing}
                                className="btn-secondary flex items-center gap-2"
                            >
                                <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
                                <span>Refresh All</span>
                            </button>
                            <button className="btn-primary flex items-center gap-2">
                                <Download className="w-4 h-4" />
                                <span>Export Report</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="p-6 space-y-6">
                {/* Summary Cards */}
                <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-foreground-muted">Average Security Score</span>
                            <HealthGradeBadge score={data.average_security_score} />
                        </div>
                        <div className="text-3xl font-bold text-foreground-primary">
                            {data.average_security_score.toFixed(1)}%
                        </div>
                    </div>

                    <div className="card">
                        <div className="text-sm text-foreground-muted mb-2">Tenant Status</div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-status-success" />
                                <span className="text-lg font-semibold text-foreground-primary">{data.healthy_tenants}</span>
                                <span className="text-sm text-foreground-muted">Healthy</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-status-warning" />
                                <span className="text-lg font-semibold text-foreground-primary">{data.warning_tenants}</span>
                                <span className="text-sm text-foreground-muted">Warning</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-status-error" />
                                <span className="text-lg font-semibold text-foreground-primary">{data.critical_tenants}</span>
                                <span className="text-sm text-foreground-muted">Critical</span>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-foreground-muted">Total Critical Risks</span>
                            <AlertTriangle className="w-5 h-5 text-status-error" />
                        </div>
                        <div className="text-3xl font-bold text-status-error">
                            {data.total_critical_risks}
                        </div>
                        <p className="text-sm text-foreground-muted mt-1">
                            +{data.total_high_risks} high severity
                        </p>
                    </div>

                    <div className="card">
                        <div className="text-sm text-foreground-muted mb-2">Active Alerts</div>
                        <div className="text-3xl font-bold text-foreground-primary">
                            {data.total_active_alerts}
                        </div>
                        <p className="text-sm text-foreground-muted mt-1">
                            Across all tenants
                        </p>
                    </div>
                </section>

                {/* Cross-Tenant Alerts */}
                <section className="card">
                    <h2 className="section-title mb-4">Priority Alerts</h2>
                    <div className="space-y-3">
                        {crossTenantAlerts.map((alert) => (
                            <div
                                key={alert.id}
                                className="flex items-center justify-between p-3 rounded-lg bg-background-tertiary"
                            >
                                <div className="flex items-center gap-3">
                                    <div className={cn(
                                        'w-2 h-2 rounded-full',
                                        alert.severity === 'critical' ? 'bg-status-error' : 'bg-status-warning'
                                    )} />
                                    <span className="text-sm font-medium text-foreground-primary">
                                        {alert.title}
                                    </span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-foreground-muted">
                                        {alert.tenant_count} tenant{alert.tenant_count > 1 ? 's' : ''}
                                    </span>
                                    <button className="text-accent hover:text-accent-dark text-sm font-medium flex items-center gap-1">
                                        View Details
                                        <ExternalLink className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Tenant Ranking Table */}
                <TenantRankingTable tenants={data.tenants} />
            </main>
        </div>
    )
}
