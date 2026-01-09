'use client'

import { useState } from 'react'
import { cn, getTimeAgo } from '@/lib/utils'
import {
    UserMinus,
    CheckCircle2,
    XCircle,
    Clock,
    AlertCircle,
    ChevronDown,
    ChevronRight,
    Shield,
    Laptop,
    Key,
    Users,
    Mail
} from 'lucide-react'

interface OffboardedUser {
    user_id: string
    display_name: string
    email: string
    department: string
    terminated_date: string
    processed_date: string
    status: 'complete' | 'in_progress' | 'pending' | 'failed'
    checks: {
        account_disabled: boolean
        mfa_removed: boolean
        groups_removed: boolean
        licenses_revoked: boolean
        devices_wiped: boolean
        mailbox_converted: boolean
    }
}

// Mock data
const mockOffboardedUsers: OffboardedUser[] = [
    {
        user_id: 'off-001',
        display_name: 'John Thompson',
        email: 'john.thompson@company.com',
        department: 'Sales',
        terminated_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        processed_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'complete',
        checks: {
            account_disabled: true,
            mfa_removed: true,
            groups_removed: true,
            licenses_revoked: true,
            devices_wiped: true,
            mailbox_converted: true,
        },
    },
    {
        user_id: 'off-002',
        display_name: 'Emily Chen',
        email: 'emily.chen@company.com',
        department: 'Marketing',
        terminated_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        processed_date: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
        status: 'in_progress',
        checks: {
            account_disabled: true,
            mfa_removed: true,
            groups_removed: true,
            licenses_revoked: true,
            devices_wiped: false,
            mailbox_converted: false,
        },
    },
    {
        user_id: 'off-003',
        display_name: 'Michael Rodriguez',
        email: 'michael.rodriguez@company.com',
        department: 'Engineering',
        terminated_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        processed_date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'complete',
        checks: {
            account_disabled: true,
            mfa_removed: true,
            groups_removed: true,
            licenses_revoked: true,
            devices_wiped: true,
            mailbox_converted: true,
        },
    },
    {
        user_id: 'off-004',
        display_name: 'Sarah Kim',
        email: 'sarah.kim@company.com',
        department: 'Finance',
        terminated_date: new Date().toISOString(),
        processed_date: new Date().toISOString(),
        status: 'pending',
        checks: {
            account_disabled: false,
            mfa_removed: false,
            groups_removed: false,
            licenses_revoked: false,
            devices_wiped: false,
            mailbox_converted: false,
        },
    },
]

const checkLabels = {
    account_disabled: { label: 'Account Disabled', icon: Shield },
    mfa_removed: { label: 'MFA Removed', icon: Key },
    groups_removed: { label: 'Groups Removed', icon: Users },
    licenses_revoked: { label: 'Licenses Revoked', icon: CheckCircle2 },
    devices_wiped: { label: 'Devices Wiped', icon: Laptop },
    mailbox_converted: { label: 'Mailbox Converted', icon: Mail },
}

export function OffboardingStatus({ className }: { className?: string }) {
    const [expandedUser, setExpandedUser] = useState<string | null>(null)
    const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'complete'>('all')

    const filteredUsers = filter === 'all'
        ? mockOffboardedUsers
        : mockOffboardedUsers.filter(u => u.status === filter)

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'complete': return <CheckCircle2 className="w-5 h-5 text-status-success" />
            case 'in_progress': return <Clock className="w-5 h-5 text-status-warning" />
            case 'pending': return <AlertCircle className="w-5 h-5 text-foreground-muted" />
            case 'failed': return <XCircle className="w-5 h-5 text-status-error" />
            default: return null
        }
    }

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'complete': return 'Complete'
            case 'in_progress': return 'In Progress'
            case 'pending': return 'Pending'
            case 'failed': return 'Failed'
            default: return status
        }
    }

    const getCompletedChecks = (user: OffboardedUser) => {
        const total = Object.keys(user.checks).length
        const completed = Object.values(user.checks).filter(Boolean).length
        return { completed, total }
    }

    return (
        <div className={cn('card', className)}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="section-title flex items-center gap-2">
                    <UserMinus className="w-5 h-5" />
                    <span>Recent Offboarding</span>
                </h3>

                {/* Filter */}
                <div className="flex items-center gap-2">
                    {(['all', 'pending', 'in_progress', 'complete'] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={cn(
                                'px-3 py-1 text-xs font-medium rounded-full transition-colors capitalize',
                                filter === f
                                    ? 'bg-accent text-foreground-primary'
                                    : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
                            )}
                        >
                            {f === 'all' ? 'All' : f.replace('_', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            <div className="space-y-3">
                {filteredUsers.map((user) => {
                    const { completed, total } = getCompletedChecks(user)
                    const isExpanded = expandedUser === user.user_id

                    return (
                        <div
                            key={user.user_id}
                            className="border border-divider rounded-lg overflow-hidden"
                        >
                            {/* Header */}
                            <button
                                onClick={() => setExpandedUser(isExpanded ? null : user.user_id)}
                                className="w-full flex items-center gap-4 p-4 hover:bg-background-tertiary/50 transition-colors"
                            >
                                {isExpanded ? (
                                    <ChevronDown className="w-4 h-4 text-foreground-muted" />
                                ) : (
                                    <ChevronRight className="w-4 h-4 text-foreground-muted" />
                                )}

                                {getStatusIcon(user.status)}

                                <div className="flex-1 text-left">
                                    <p className="text-sm font-medium text-foreground-primary">
                                        {user.display_name}
                                    </p>
                                    <p className="text-xs text-foreground-muted">
                                        {user.department} • Terminated {getTimeAgo(user.terminated_date)}
                                    </p>
                                </div>

                                <div className="text-right">
                                    <p className={cn(
                                        'text-sm font-medium',
                                        completed === total ? 'text-status-success' : 'text-foreground-secondary'
                                    )}>
                                        {completed}/{total} checks
                                    </p>
                                    <p className="text-xs text-foreground-muted">
                                        {getStatusLabel(user.status)}
                                    </p>
                                </div>
                            </button>

                            {/* Expanded Details */}
                            {isExpanded && (
                                <div className="px-4 pb-4 pt-2 border-t border-divider bg-background-tertiary/30">
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {Object.entries(user.checks).map(([key, value]) => {
                                            const checkInfo = checkLabels[key as keyof typeof checkLabels]
                                            const Icon = checkInfo.icon

                                            return (
                                                <div
                                                    key={key}
                                                    className={cn(
                                                        'flex items-center gap-2 p-2 rounded-lg',
                                                        value ? 'bg-status-success/10' : 'bg-background-tertiary'
                                                    )}
                                                >
                                                    {value ? (
                                                        <CheckCircle2 className="w-4 h-4 text-status-success" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-foreground-muted" />
                                                    )}
                                                    <span className={cn(
                                                        'text-sm',
                                                        value ? 'text-foreground-primary' : 'text-foreground-muted'
                                                    )}>
                                                        {checkInfo.label}
                                                    </span>
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
