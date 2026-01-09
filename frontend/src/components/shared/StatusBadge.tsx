'use client'

import { cn } from '@/lib/utils'
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'

interface StatusBadgeProps {
  status: 'healthy' | 'warning' | 'critical' | 'unknown' | string
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  className?: string
}

export function StatusBadge({
  status,
  label,
  size = 'md',
  showIcon = true,
  className,
}: StatusBadgeProps) {
  const statusConfig = {
    healthy: {
      icon: CheckCircle2,
      bg: 'bg-status-success/20',
      text: 'text-status-success',
      border: 'border-status-success/30',
      label: 'Healthy',
    },
    success: {
      icon: CheckCircle2,
      bg: 'bg-status-success/20',
      text: 'text-status-success',
      border: 'border-status-success/30',
      label: 'Success',
    },
    warning: {
      icon: AlertTriangle,
      bg: 'bg-status-warning/20',
      text: 'text-status-warning',
      border: 'border-status-warning/30',
      label: 'Warning',
    },
    critical: {
      icon: XCircle,
      bg: 'bg-status-error/20',
      text: 'text-status-error',
      border: 'border-status-error/30',
      label: 'Critical',
    },
    error: {
      icon: XCircle,
      bg: 'bg-status-error/20',
      text: 'text-status-error',
      border: 'border-status-error/30',
      label: 'Error',
    },
    unknown: {
      icon: HelpCircle,
      bg: 'bg-background-tertiary',
      text: 'text-foreground-muted',
      border: 'border-border-DEFAULT',
      label: 'Unknown',
    },
  }

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.unknown
  const Icon = config.icon

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
    lg: 'px-4 py-1.5 text-base gap-2',
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full border',
        config.bg,
        config.text,
        config.border,
        sizeClasses[size],
        className
      )}
    >
      {showIcon && <Icon className={iconSizes[size]} />}
      <span>{label || config.label}</span>
    </span>
  )
}

// Severity badge variant
interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'informational' | string
  count?: number
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function SeverityBadge({
  severity,
  count,
  size = 'md',
  className,
}: SeverityBadgeProps) {
  const severityConfig = {
    critical: {
      bg: 'bg-severity-critical/20',
      text: 'text-severity-critical',
      border: 'border-severity-critical/30',
    },
    high: {
      bg: 'bg-severity-high/20',
      text: 'text-severity-high',
      border: 'border-severity-high/30',
    },
    medium: {
      bg: 'bg-severity-medium/20',
      text: 'text-severity-medium',
      border: 'border-severity-medium/30',
    },
    low: {
      bg: 'bg-severity-low/20',
      text: 'text-severity-low',
      border: 'border-severity-low/30',
    },
    informational: {
      bg: 'bg-severity-info/20',
      text: 'text-severity-info',
      border: 'border-severity-info/30',
    },
  }

  const config = severityConfig[severity as keyof typeof severityConfig] || severityConfig.low

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-full border capitalize',
        config.bg,
        config.text,
        config.border,
        sizeClasses[size],
        className
      )}
    >
      {count !== undefined && (
        <span className="font-bold">{count}</span>
      )}
      <span>{severity}</span>
    </span>
  )
}
