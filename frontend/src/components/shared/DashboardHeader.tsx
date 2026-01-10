'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Shield, RefreshCw, Download, Clock, Eye, EyeOff } from 'lucide-react'
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

interface Tenant {
  id: string
  name: string
  securityScore?: number
  status?: 'healthy' | 'warning' | 'critical'
}

export function DashboardHeader({
  tenantName,
  tenantId = 'demo',
  title,
  lastUpdated: _lastUpdated,
  minutesAgo,
  onRefresh,
  isRefreshing,
  className,
}: DashboardHeaderProps) {
  void _lastUpdated // Available for future display enhancement
  const [isExportModalOpen, setIsExportModalOpen] = useState(false)
  const { isSimplified, toggleViewMode } = useViewMode()
  const router = useRouter()
  const _pathname = usePathname()
  void _pathname // Available for route-based logic
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [isLoadingTenants, setIsLoadingTenants] = useState(true)

  useEffect(() => {
    const fetchTenants = async () => {
      try {
        const { apiClient } = await import('@/lib/api-client')
        const data = await apiClient.listTenants()
        if (Array.isArray(data)) {
          setTenants(data)
        }
      } catch (error) {
        console.error('Failed to fetch tenants:', error)
        // Fallback to demo if fetch fails
        setTenants([{ id: 'demo', name: 'Demo Organization', securityScore: 72.5, status: 'warning' }])
      } finally {
        setIsLoadingTenants(false)
      }
    }
    fetchTenants()
  }, [])


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

              {/* TenantSwitcher */}
              <TenantSwitcher
                currentTenant={{ id: tenantId, name: tenantName, status: 'healthy' }}
                tenants={tenants}
                onSwitch={(id) => router.push(`/${id}/${dashboardType}`)}
                isLoading={isLoadingTenants}
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
            <NavTab href={`/${tenantId}/executive`} active={title.includes('Executive')}>
              Executive View
            </NavTab>
            <NavTab href={`/${tenantId}/it-staff`} active={title.includes('IT Staff')}>
              IT Staff View
            </NavTab>
            <NavTab href={`/${tenantId}/compliance`} active={title.includes('Compliance')}>
              Compliance View
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
    <Link
      href={href}
      className={cn(
        'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
        active
          ? 'bg-accent text-foreground-primary'
          : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
      )}
    >
      {children}
    </Link>
  )
}
