'use client'

import { useState } from 'react'
import { cn, getTimeAgo } from '@/lib/utils'
import { SeverityBadge } from '@/components/shared/StatusBadge'
import { DataTable } from './DataTable'
import { Bell, Filter } from 'lucide-react'

interface Alert {
  id: string
  title: string
  description: string
  severity: string
  status: string
  category: string
  resource_name: string
  resource_type: string
  created_at: string
}

interface AlertQueueProps {
  alerts: Alert[]
  className?: string
}

export function AlertQueue({ alerts, className }: AlertQueueProps) {
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter !== 'all' && alert.severity.toLowerCase() !== severityFilter) return false
    if (statusFilter !== 'all' && alert.status.toLowerCase() !== statusFilter) return false
    return true
  })

  const columns = [
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      render: (alert: Alert) => (
        <SeverityBadge severity={alert.severity} size="sm" />
      ),
    },
    {
      key: 'title',
      header: 'Alert',
      sortable: true,
      render: (alert: Alert) => (
        <div>
          <p className="font-medium text-foreground-primary">{alert.title}</p>
          <p className="text-xs text-foreground-muted mt-0.5">{alert.category}</p>
        </div>
      ),
    },
    {
      key: 'resource_name',
      header: 'Resource',
      sortable: true,
      render: (alert: Alert) => (
        <div>
          <p className="text-foreground-primary">{alert.resource_name}</p>
          <p className="text-xs text-foreground-muted">{alert.resource_type}</p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (alert: Alert) => (
        <span className={cn(
          'px-2 py-1 rounded text-xs font-medium capitalize',
          alert.status === 'active' && 'bg-status-error/20 text-status-error',
          alert.status === 'investigating' && 'bg-status-warning/20 text-status-warning',
          alert.status === 'resolved' && 'bg-status-success/20 text-status-success',
        )}>
          {alert.status}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Age',
      sortable: true,
      render: (alert: Alert) => (
        <span className="text-foreground-muted">{getTimeAgo(alert.created_at)}</span>
      ),
    },
  ]

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title flex items-center gap-2">
          <Bell className="w-5 h-5 text-accent" />
          Alert Queue
        </h3>
        <div className="flex items-center gap-2">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="input text-sm py-1"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input text-sm py-1"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <DataTable
        data={filteredAlerts}
        columns={columns}
        searchKeys={['title', 'resource_name', 'category']}
        pageSize={10}
      />
    </div>
  )
}
