'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ExternalLink, ChevronUp, ChevronDown, ArrowUpDown } from 'lucide-react'
import { HealthGradeBadge } from '@/components/executive/HealthGrade'

interface Tenant {
    tenant_id: string
    tenant_name: string
    security_score: number
    compliance_score: number
    critical_risks: number
    high_risks: number
    mfa_coverage_percent: number
    device_compliance_percent: number
    backup_health_percent: number
    active_alerts: number
    status: string
}

interface TenantRankingTableProps {
    tenants: Tenant[]
    className?: string
}

type SortKey = 'tenant_name' | 'security_score' | 'compliance_score' | 'critical_risks' | 'mfa_coverage_percent' | 'active_alerts'

export function TenantRankingTable({ tenants, className }: TenantRankingTableProps) {
    const [sortKey, setSortKey] = useState<SortKey>('security_score')
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

    const handleSort = (key: SortKey) => {
        if (key === sortKey) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
        } else {
            setSortKey(key)
            setSortOrder('asc')
        }
    }

    const sortedTenants = [...tenants].sort((a, b) => {
        let aVal = a[sortKey]
        let bVal = b[sortKey]

        if (typeof aVal === 'string' && typeof bVal === 'string') {
            return sortOrder === 'asc'
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal)
        }

        return sortOrder === 'asc'
            ? (aVal as number) - (bVal as number)
            : (bVal as number) - (aVal as number)
    })

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'bg-status-success'
            case 'warning': return 'bg-status-warning'
            case 'critical': return 'bg-status-error'
            default: return 'bg-foreground-muted'
        }
    }

    const SortHeader = ({ label, sortKeyVal }: { label: string; sortKeyVal: SortKey }) => (
        <button
            onClick={() => handleSort(sortKeyVal)}
            className="flex items-center gap-1 hover:text-foreground-primary transition-colors"
        >
            <span>{label}</span>
            {sortKey === sortKeyVal ? (
                sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
            ) : (
                <ArrowUpDown className="w-3 h-3 opacity-50" />
            )}
        </button>
    )

    return (
        <div className={cn('card overflow-hidden', className)}>
            <div className="flex items-center justify-between mb-4">
                <h2 className="section-title">Tenant Rankings</h2>
                <span className="text-sm text-foreground-muted">
                    Sorted by {sortKey.replace('_', ' ')} ({sortOrder})
                </span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-divider">
                            <th className="text-left py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="Tenant" sortKeyVal="tenant_name" />
                            </th>
                            <th className="text-center py-3 px-4 text-sm font-medium text-foreground-muted">
                                Grade
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="Security" sortKeyVal="security_score" />
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="Compliance" sortKeyVal="compliance_score" />
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="Critical" sortKeyVal="critical_risks" />
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="MFA" sortKeyVal="mfa_coverage_percent" />
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                <SortHeader label="Alerts" sortKeyVal="active_alerts" />
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedTenants.map((tenant, index) => (
                            <tr
                                key={tenant.tenant_id}
                                className={cn(
                                    'border-b border-divider/50 hover:bg-background-tertiary/50 transition-colors',
                                    index === sortedTenants.length - 1 && 'border-b-0'
                                )}
                            >
                                <td className="py-3 px-4">
                                    <div className="flex items-center gap-3">
                                        <div className={cn('w-2 h-2 rounded-full', getStatusColor(tenant.status))} />
                                        <span className="text-sm font-medium text-foreground-primary">
                                            {tenant.tenant_name}
                                        </span>
                                    </div>
                                </td>
                                <td className="py-3 px-4 text-center">
                                    <HealthGradeBadge score={tenant.security_score} />
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <span className={cn(
                                        'text-sm font-medium',
                                        tenant.security_score >= 80 ? 'text-status-success' :
                                            tenant.security_score >= 60 ? 'text-foreground-primary' :
                                                'text-status-error'
                                    )}>
                                        {tenant.security_score.toFixed(1)}%
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <span className="text-sm text-foreground-primary">
                                        {tenant.compliance_score.toFixed(1)}%
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <span className={cn(
                                        'text-sm font-medium',
                                        tenant.critical_risks > 0 ? 'text-status-error' : 'text-status-success'
                                    )}>
                                        {tenant.critical_risks}
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <span className={cn(
                                        'text-sm',
                                        tenant.mfa_coverage_percent >= 90 ? 'text-status-success' :
                                            tenant.mfa_coverage_percent >= 70 ? 'text-foreground-primary' :
                                                'text-status-error'
                                    )}>
                                        {tenant.mfa_coverage_percent.toFixed(0)}%
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <span className="text-sm text-foreground-primary">
                                        {tenant.active_alerts}
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <a
                                        href={`/${tenant.tenant_id}/executive`}
                                        className="text-accent hover:text-accent-dark text-sm font-medium flex items-center justify-end gap-1"
                                    >
                                        View
                                        <ExternalLink className="w-3 h-3" />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
