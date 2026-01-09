import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  return value.toString()
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function getTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-severity-critical'
    case 'high':
      return 'text-severity-high'
    case 'medium':
      return 'text-severity-medium'
    case 'low':
      return 'text-severity-low'
    default:
      return 'text-foreground-secondary'
  }
}

export function getSeverityBgColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-severity-critical/20'
    case 'high':
      return 'bg-severity-high/20'
    case 'medium':
      return 'bg-severity-medium/20'
    case 'low':
      return 'bg-severity-low/20'
    default:
      return 'bg-background-tertiary'
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'healthy':
    case 'success':
    case 'compliant':
      return 'text-status-success'
    case 'warning':
      return 'text-status-warning'
    case 'critical':
    case 'error':
    case 'non_compliant':
      return 'text-status-error'
    default:
      return 'text-foreground-muted'
  }
}

export function getTrendColor(direction: string): string {
  switch (direction) {
    case 'up':
      return 'text-status-success'
    case 'down':
      return 'text-status-error'
    default:
      return 'text-foreground-muted'
  }
}
