'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Shield, RefreshCw, Download, ChevronDown, Clock, Eye, EyeOff } from 'lucide-react'
import { ExportModal } from './ExportModal'
import { TenantSwitcher } from './TenantSwitcher'
import { useViewMode } from '@/hooks/useViewMode'

interface DashboardHeaderProps {
  tenantName: string
  tenantId?: string
  title: string
  lastUpdated?: string
  minutesAgo?: number
  onRefresh?: () => void
  isRefreshing?: boolean
  className?: string
}

export function DashboardHeader({
  tenantName,
  tenantId = 'demo',
  title,
  lastUpdated,
  minutesAgo,
  onRefresh,
  isRefreshing,
  className,
}: DashboardHeaderProps) {
  const [isExportModalOpen, setIsExportModalOpen] = useState(false)
  const { isSimplified, toggleViewMode } = useViewMode()
  const pathname = usePathname()

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

  const dashboardType = title.includes('IT Staff') ? 'it-staff' : 'executive'

  return (
    <>
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

              {/* Tenant Switcher */}
              <TenantSwitcher
                currentTenant={{ id: tenantId, name: tenantName, status: 'healthy' }}
                tenants={[
                  { id: 'demo', name: 'Demo Organization', securityScore: 72.5, status: 'warning' },
                  { id: 'acme-corp', name: 'Acme Corporation', securityScore: 85.2, status: 'healthy' },
                  { id: 'globex', name: 'Globex Industries', securityScore: 58.1, status: 'critical' },
                  { id: 'initech', name: 'Initech Solutions', securityScore: 91.0, status: 'healthy' },
                ]}
                onSwitch={(id) => { window.location.href = `/${id}/executive` }}
              />
            </div>

            {/* Right: Actions and Status */}
            <div className="flex items-center gap-4">
              {/* Simplified View Toggle */}
              <button
                onClick={toggleViewMode}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isSimplified
                    ? 'bg-accent/10 text-accent'
                    : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
                )}
                title={isSimplified ? 'Switch to Technical View' : 'Switch to Simple View'}
              >
                {isSimplified ? (
                  <>
                    <Eye className="w-4 h-4" />
                    <span>Simple</span>
                  </>
                ) : (
                  <>
                    <EyeOff className="w-4 h-4" />
                    <span>Technical</span>
                  </>
                )}
              </button>

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
              <button
                onClick={() => setIsExportModalOpen(true)}
                className="btn-primary flex items-center gap-2"
              >
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

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        tenantId={tenantId}
        dashboardType={dashboardType}
      />
    </>
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
