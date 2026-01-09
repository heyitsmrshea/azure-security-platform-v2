'use client'

import { cn } from '@/lib/utils'
import { Shield, RefreshCw, Download, ChevronDown, Clock } from 'lucide-react'

interface DashboardHeaderProps {
  tenantName: string
  title: string
  lastUpdated?: string
  minutesAgo?: number
  onRefresh?: () => void
  isRefreshing?: boolean
  className?: string
}

export function DashboardHeader({
  tenantName,
  title,
  lastUpdated,
  minutesAgo,
  onRefresh,
  isRefreshing,
  className,
}: DashboardHeaderProps) {
  const getFreshnessStatus = () => {
    if (!minutesAgo) return 'unknown'
    if (minutesAgo <= 15) return 'fresh'
    if (minutesAgo <= 60) return 'stale'
    return 'outdated'
  }

  const freshnessStatus = getFreshnessStatus()
  const freshnessColors = {
    fresh: 'text-status-success',
    stale: 'text-status-warning',
    outdated: 'text-status-error',
    unknown: 'text-foreground-muted',
  }

  return (
    <header className={cn('border-b border-divider bg-background-secondary', className)}>
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Logo and Navigation */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-accent" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-foreground-primary">
                  Security Dashboard
                </h1>
                <p className="text-sm text-foreground-muted">{title}</p>
              </div>
            </div>

            {/* Tenant Selector */}
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-background-tertiary hover:bg-divider transition-colors">
              <span className="text-sm font-medium text-foreground-primary">
                {tenantName}
              </span>
              <ChevronDown className="w-4 h-4 text-foreground-muted" />
            </button>
          </div>

          {/* Right: Actions and Status */}
          <div className="flex items-center gap-4">
            {/* Data Freshness Indicator */}
            {minutesAgo !== undefined && (
              <div className={cn('flex items-center gap-2 text-sm', freshnessColors[freshnessStatus])}>
                <Clock className="w-4 h-4" />
                <span>
                  {minutesAgo < 1
                    ? 'Just now'
                    : minutesAgo < 60
                    ? `${minutesAgo}m ago`
                    : `${Math.floor(minutesAgo / 60)}h ago`}
                </span>
              </div>
            )}

            {/* Refresh Button */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isRefreshing}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
                <span>Refresh</span>
              </button>
            )}

            {/* Export Button */}
            <button className="btn-primary flex items-center gap-2">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 mt-4">
          <NavTab href="/demo/executive" active={title.includes('Executive')}>
            Executive View
          </NavTab>
          <NavTab href="/demo/it-staff" active={title.includes('IT Staff')}>
            IT Staff View
          </NavTab>
        </nav>
      </div>
    </header>
  )
}

interface NavTabProps {
  href: string
  active?: boolean
  children: React.ReactNode
}

function NavTab({ href, active, children }: NavTabProps) {
  return (
    <a
      href={href}
      className={cn(
        'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
        active
          ? 'bg-accent text-foreground-primary'
          : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
      )}
    >
      {children}
    </a>
  )
}
