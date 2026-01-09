'use client'

import { cn, getTimeAgo } from '@/lib/utils'
import { DataTable } from './DataTable'
import { FileText, AlertTriangle } from 'lucide-react'

interface AuditLog {
  id: string
  activity: string
  category: string
  initiated_by: string
  target_resource: string
  result: string
  timestamp: string
  details?: Record<string, any>
}

interface AuditTrailProps {
  logs: AuditLog[]
  title?: string
  className?: string
}

export function AuditTrail({ logs, title = 'Recent Admin Actions', className }: AuditTrailProps) {
  const columns = [
    {
      key: 'timestamp',
      header: 'Time',
      sortable: true,
      render: (log: AuditLog) => (
        <span className="text-foreground-muted whitespace-nowrap">
          {getTimeAgo(log.timestamp)}
        </span>
      ),
    },
    {
      key: 'activity',
      header: 'Activity',
      sortable: true,
      render: (log: AuditLog) => (
        <div>
          <p className="font-medium text-foreground-primary">{log.activity}</p>
          <p className="text-xs text-foreground-muted">{log.category}</p>
        </div>
      ),
    },
    {
      key: 'initiated_by',
      header: 'Initiated By',
      sortable: true,
      render: (log: AuditLog) => (
        <span className="text-foreground-secondary">{log.initiated_by}</span>
      ),
    },
    {
      key: 'target_resource',
      header: 'Target',
      sortable: true,
      render: (log: AuditLog) => (
        <span className="text-foreground-secondary">{log.target_resource}</span>
      ),
    },
    {
      key: 'result',
      header: 'Result',
      sortable: true,
      render: (log: AuditLog) => (
        <span className={cn(
          'px-2 py-1 rounded text-xs font-medium capitalize',
          log.result === 'success' && 'bg-status-success/20 text-status-success',
          log.result === 'failure' && 'bg-status-error/20 text-status-error',
        )}>
          {log.result}
        </span>
      ),
    },
  ]

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title flex items-center gap-2">
          <FileText className="w-5 h-5 text-accent" />
          {title}
        </h3>
      </div>

      <DataTable
        data={logs}
        columns={columns}
        searchKeys={['activity', 'initiated_by', 'target_resource']}
        pageSize={10}
      />
    </div>
  )
}

interface HighRiskOperation {
  operation: string
  initiated_by: string
  target: string
  timestamp: string
  risk_reason: string
}

interface HighRiskOperationsProps {
  operations: HighRiskOperation[]
  className?: string
}

export function HighRiskOperations({ operations, className }: HighRiskOperationsProps) {
  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-severity-high" />
          High-Risk Operations
        </h3>
      </div>

      <div className="space-y-3">
        {operations.map((op, index) => (
          <div
            key={index}
            className="p-3 rounded-lg bg-severity-high/10 border border-severity-high/20"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-medium text-foreground-primary">{op.operation}</p>
                <p className="text-sm text-foreground-secondary mt-1">
                  Target: {op.target}
                </p>
                <p className="text-xs text-severity-high mt-1">
                  {op.risk_reason}
                </p>
              </div>
              <div className="text-right text-sm">
                <p className="text-foreground-muted">{getTimeAgo(op.timestamp)}</p>
                <p className="text-foreground-secondary">{op.initiated_by}</p>
              </div>
            </div>
          </div>
        ))}

        {operations.length === 0 && (
          <p className="text-center text-foreground-muted py-4">
            No high-risk operations detected
          </p>
        )}
      </div>
    </div>
  )
}
