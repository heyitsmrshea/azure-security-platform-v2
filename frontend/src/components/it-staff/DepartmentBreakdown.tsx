'use client'

import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, Users, Laptop } from 'lucide-react'
import { useState } from 'react'

interface DepartmentMetric {
    department: string
    total: number
    compliant: number
    nonCompliant: number
    percentage: number
}

interface DepartmentBreakdownProps {
    title: string
    icon?: React.ReactNode
    data: DepartmentMetric[]
    type: 'mfa' | 'device'
    className?: string
}

export function DepartmentBreakdown({
    title,
    icon,
    data,
    type,
    className,
}: DepartmentBreakdownProps) {
    const [expandedDept, setExpandedDept] = useState<string | null>(null)

    // Sort by percentage (lowest first to highlight issues)
    const sortedData = [...data].sort((a, b) => a.percentage - b.percentage)

    const getStatusColor = (percentage: number) => {
        if (percentage >= 90) return 'bg-status-success'
        if (percentage >= 70) return 'bg-status-warning'
        return 'bg-status-error'
    }

    const getTextColor = (percentage: number) => {
        if (percentage >= 90) return 'text-status-success'
        if (percentage >= 70) return 'text-status-warning'
        return 'text-status-error'
    }

    return (
        <div className={cn('card', className)}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="section-title flex items-center gap-2">
                    {icon || (type === 'mfa' ? <Users className="w-5 h-5" /> : <Laptop className="w-5 h-5" />)}
                    <span>{title}</span>
                </h3>
                <span className="text-sm text-foreground-muted">
                    {data.length} departments
                </span>
            </div>

            <div className="space-y-3">
                {sortedData.map((dept) => (
                    <div key={dept.department} className="space-y-2">
                        <button
                            onClick={() => setExpandedDept(expandedDept === dept.department ? null : dept.department)}
                            className="w-full flex items-center gap-3 group"
                        >
                            {expandedDept === dept.department ? (
                                <ChevronDown className="w-4 h-4 text-foreground-muted" />
                            ) : (
                                <ChevronRight className="w-4 h-4 text-foreground-muted" />
                            )}

                            <div className="flex-1 text-left">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium text-foreground-primary group-hover:text-accent transition-colors">
                                        {dept.department}
                                    </span>
                                    <span className={cn('text-sm font-medium', getTextColor(dept.percentage))}>
                                        {dept.percentage.toFixed(0)}%
                                    </span>
                                </div>
                                <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
                                    <div
                                        className={cn('h-full rounded-full transition-all', getStatusColor(dept.percentage))}
                                        style={{ width: `${dept.percentage}%` }}
                                    />
                                </div>
                            </div>
                        </button>

                        {/* Expanded Details */}
                        {expandedDept === dept.department && (
                            <div className="ml-7 pl-3 border-l-2 border-divider space-y-2 py-2 animate-in fade-in duration-200">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-foreground-secondary">Total {type === 'mfa' ? 'Users' : 'Devices'}</span>
                                    <span className="text-foreground-primary font-medium">{dept.total}</span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-foreground-secondary">
                                        {type === 'mfa' ? 'With MFA' : 'Compliant'}
                                    </span>
                                    <span className="text-status-success font-medium">{dept.compliant}</span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-foreground-secondary">
                                        {type === 'mfa' ? 'Without MFA' : 'Non-Compliant'}
                                    </span>
                                    <span className="text-status-error font-medium">{dept.nonCompliant}</span>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

// Mock data helper
export const mockMFAByDepartment: DepartmentMetric[] = [
    { department: 'Engineering', total: 45, compliant: 43, nonCompliant: 2, percentage: 95.6 },
    { department: 'Sales', total: 32, compliant: 28, nonCompliant: 4, percentage: 87.5 },
    { department: 'Marketing', total: 18, compliant: 14, nonCompliant: 4, percentage: 77.8 },
    { department: 'Finance', total: 12, compliant: 12, nonCompliant: 0, percentage: 100 },
    { department: 'HR', total: 8, compliant: 7, nonCompliant: 1, percentage: 87.5 },
    { department: 'Operations', total: 25, compliant: 19, nonCompliant: 6, percentage: 76 },
    { department: 'Legal', total: 6, compliant: 6, nonCompliant: 0, percentage: 100 },
    { department: 'Executive', total: 4, compliant: 4, nonCompliant: 0, percentage: 100 },
]

export const mockDevicesByDepartment: DepartmentMetric[] = [
    { department: 'Engineering', total: 52, compliant: 49, nonCompliant: 3, percentage: 94.2 },
    { department: 'Sales', total: 38, compliant: 35, nonCompliant: 3, percentage: 92.1 },
    { department: 'Marketing', total: 20, compliant: 17, nonCompliant: 3, percentage: 85 },
    { department: 'Finance', total: 14, compliant: 13, nonCompliant: 1, percentage: 92.9 },
    { department: 'HR', total: 10, compliant: 9, nonCompliant: 1, percentage: 90 },
    { department: 'Operations', total: 28, compliant: 22, nonCompliant: 6, percentage: 78.6 },
    { department: 'Legal', total: 7, compliant: 7, nonCompliant: 0, percentage: 100 },
    { department: 'Executive', total: 6, compliant: 6, nonCompliant: 0, percentage: 100 },
]
