'use client'

import { ReactNode } from 'react'
import { cn, getTrendColor, formatNumber } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { TrendDirection } from '@/types/dashboard'

interface MetricCardProps {
  label: string
  value: string | number
  trend?: {
    direction: TrendDirection
    change_value: number
    change_percent?: number
  }
  comparison?: string
  icon?: ReactNode
  status?: 'healthy' | 'warning' | 'critical' | 'neutral'
  className?: string
  size?: 'default' | 'large'
  isNotConfigured?: boolean
  actionLink?: string
  actionLabel?: string
}

export function MetricCard({
  label,
  value,
  trend,
  comparison,
  icon,
  status = 'neutral',
  className,
  size = 'default',
  isNotConfigured = false,
  actionLink,
  actionLabel = 'View details',
}: MetricCardProps) {
  const statusColors = {
    healthy: 'border-l-status-success',
    warning: 'border-l-status-warning',
    critical: 'border-l-status-error',
    neutral: 'border-l-transparent',
  }

  const effectiveStatus = isNotConfigured ? 'neutral' : status

  const TrendIcon = trend?.direction === 'up'
    ? TrendingUp
    : trend?.direction === 'down'
      ? TrendingDown
      : Minus

  const content = (
    <>
      <div className="flex items-start justify-between mb-3">
        <span className="kpi-label">{label}</span>
        {icon && (
          <div className="text-foreground-muted">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-end justify-between">
        <div>
          <div className={cn(
            'font-bold tracking-tight',
            size === 'large' ? 'text-5xl' : 'text-4xl',
            isNotConfigured ? 'text-foreground-muted text-2xl font-normal' : 'text-foreground-primary'
          )}>
            {isNotConfigured ? 'Not Configured' : (typeof value === 'number' ? formatNumber(value) : value)}
          </div>

          {comparison && !isNotConfigured && (
            <div className="mt-1 text-sm text-foreground-muted">
              {comparison}
            </div>
          )}

          {isNotConfigured && actionLink && (
            <div className="mt-2 text-xs text-accent font-medium flex items-center gap-1 group-hover:underline">
              {actionLabel} <ArrowUpRight className="w-3 h-3" />
            </div>
          )}
        </div>

        {!isNotConfigured && trend && (
          <div className={cn(
            'flex items-center gap-1 px-2 py-1 rounded-md text-sm font-medium',
            trend.direction === 'up'
              ? 'bg-status-success/10 text-status-success'
              : trend.direction === 'down'
                ? 'bg-status-error/10 text-status-error'
                : 'bg-background-tertiary text-foreground-muted'
          )}>
            <TrendIcon className="w-4 h-4" />
            <span>
              {trend.change_percent !== undefined
                ? `${Math.abs(trend.change_percent).toFixed(1)}%`
                : Math.abs(trend.change_value).toFixed(1)}
            </span>
          </div>
        )}
      </div>
    </>
  )

  if (actionLink) {
    return (
      <a
        href={actionLink}
        target="_blank"
        rel="noopener noreferrer"
        className={cn(
          'card border-l-4 transition-all duration-200 block group hover:shadow-card-hover no-underline',
          statusColors[effectiveStatus],
          className
        )}
      >
        {content}
      </a>
    )
  }

  return (
    <div
      className={cn(
        'card border-l-4 transition-all duration-200',
        statusColors[effectiveStatus],
        'hover:shadow-card-hover',
        className
      )}
    >
      {content}
    </div>
  )
}

// Specialized card for percentage metrics with progress ring
interface ScoreCardProps {
  label: string
  score: number
  maxScore?: number
  trend?: {
    direction: TrendDirection
    change_value: number
    change_percent?: number
  }
  comparison?: string
  status?: 'healthy' | 'warning' | 'critical' | 'neutral'
  className?: string
}

export function ScoreCard({
  label,
  score,
  maxScore = 100,
  trend,
  comparison,
  // status prop available for future use (e.g., border coloring)
  status: _status = 'neutral',
  className,
}: ScoreCardProps) {
  void _status // Suppress unused variable warning
  const percentage = (score / maxScore) * 100
  const circumference = 2 * Math.PI * 40
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getScoreColor = () => {
    if (percentage >= 80) return '#22C55E' // Green
    if (percentage >= 60) return '#EAB308' // Yellow
    return '#EF4444' // Red
  }

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <span className="kpi-label">{label}</span>
        {trend && (
          <div className={cn(
            'flex items-center gap-1 text-sm font-medium',
            getTrendColor(trend.direction)
          )}>
            {trend.direction === 'up' ? (
              <ArrowUpRight className="w-4 h-4" />
            ) : trend.direction === 'down' ? (
              <ArrowDownRight className="w-4 h-4" />
            ) : (
              <Minus className="w-4 h-4" />
            )}
            {Math.abs(trend.change_value).toFixed(1)}
          </div>
        )}
      </div>

      <div className="flex items-center gap-6">
        {/* Score Ring */}
        <div className="relative w-24 h-24 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background circle */}
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="none"
              stroke="#334155"
              strokeWidth="8"
            />
            {/* Progress circle */}
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="none"
              stroke={getScoreColor()}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-500 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold text-foreground-primary">
              {Math.round(score)}
            </span>
          </div>
        </div>

        {/* Details */}
        <div className="flex-1">
          <div className="text-sm text-foreground-secondary mb-1">
            {score.toFixed(1)} / {maxScore}
          </div>
          {comparison && (
            <div className="text-sm font-medium text-accent">
              {comparison}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
