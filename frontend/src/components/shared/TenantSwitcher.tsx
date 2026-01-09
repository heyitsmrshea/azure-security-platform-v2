'use client'

import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, Check, Search, Building2 } from 'lucide-react'
import { HealthGradeBadge } from '@/components/executive/HealthGrade'

interface Tenant {
    id: string
    name: string
    securityScore?: number
    status?: 'healthy' | 'warning' | 'critical'
}

interface TenantSwitcherProps {
    currentTenant: Tenant
    tenants: Tenant[]
    onSwitch: (tenantId: string) => void
    className?: string
}

export function TenantSwitcher({
    currentTenant,
    tenants,
    onSwitch,
    className,
}: TenantSwitcherProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const dropdownRef = useRef<HTMLDivElement>(null)
    const searchRef = useRef<HTMLInputElement>(null)

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    // Focus search when dropdown opens
    useEffect(() => {
        if (isOpen && searchRef.current) {
            searchRef.current.focus()
        }
    }, [isOpen])

    const filteredTenants = tenants.filter(tenant =>
        tenant.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const handleSelect = (tenantId: string) => {
        onSwitch(tenantId)
        setIsOpen(false)
        setSearchQuery('')
    }

    const getStatusColor = (status?: string) => {
        switch (status) {
            case 'healthy': return 'bg-status-success'
            case 'warning': return 'bg-status-warning'
            case 'critical': return 'bg-status-error'
            default: return 'bg-foreground-muted'
        }
    }

    return (
        <div ref={dropdownRef} className={cn('relative', className)}>
            {/* Trigger Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    'flex items-center gap-3 px-4 py-2 rounded-lg transition-colors',
                    'bg-background-tertiary hover:bg-divider',
                    isOpen && 'bg-divider'
                )}
            >
                <div className={cn('w-2 h-2 rounded-full', getStatusColor(currentTenant.status))} />
                <span className="text-sm font-medium text-foreground-primary max-w-[150px] truncate">
                    {currentTenant.name}
                </span>
                <ChevronDown className={cn(
                    'w-4 h-4 text-foreground-muted transition-transform',
                    isOpen && 'rotate-180'
                )} />
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-80 bg-background-secondary border border-divider rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    {/* Search */}
                    <div className="p-3 border-b border-divider">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-foreground-muted" />
                            <input
                                ref={searchRef}
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search tenants..."
                                className="w-full pl-10 pr-4 py-2 text-sm bg-background-tertiary border border-divider rounded-lg text-foreground-primary placeholder:text-foreground-muted focus:outline-none focus:border-accent"
                            />
                        </div>
                    </div>

                    {/* Tenant List */}
                    <div className="max-h-64 overflow-y-auto">
                        {filteredTenants.length > 0 ? (
                            filteredTenants.map((tenant) => (
                                <button
                                    key={tenant.id}
                                    onClick={() => handleSelect(tenant.id)}
                                    className={cn(
                                        'w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-background-tertiary transition-colors',
                                        tenant.id === currentTenant.id && 'bg-accent/5'
                                    )}
                                >
                                    <div className={cn('w-2 h-2 rounded-full shrink-0', getStatusColor(tenant.status))} />

                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-foreground-primary truncate">
                                            {tenant.name}
                                        </p>
                                        {tenant.securityScore !== undefined && (
                                            <p className="text-xs text-foreground-muted">
                                                Security Score: {tenant.securityScore.toFixed(1)}%
                                            </p>
                                        )}
                                    </div>

                                    {tenant.securityScore !== undefined && (
                                        <HealthGradeBadge score={tenant.securityScore} />
                                    )}

                                    {tenant.id === currentTenant.id && (
                                        <Check className="w-4 h-4 text-accent shrink-0" />
                                    )}
                                </button>
                            ))
                        ) : (
                            <div className="px-4 py-8 text-center">
                                <Building2 className="w-8 h-8 text-foreground-muted mx-auto mb-2" />
                                <p className="text-sm text-foreground-muted">No tenants found</p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    {tenants.length > 5 && (
                        <div className="px-4 py-2 border-t border-divider bg-background-tertiary/50">
                            <p className="text-xs text-foreground-muted text-center">
                                {tenants.length} tenants available
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
