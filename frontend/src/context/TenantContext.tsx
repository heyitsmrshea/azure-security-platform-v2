'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface Tenant {
    id: string
    name: string
    securityScore?: number
    status?: 'healthy' | 'warning' | 'critical'
}

interface TenantContextType {
    currentTenant: Tenant | null
    tenants: Tenant[]
    isLoading: boolean
    setCurrentTenant: (tenant: Tenant) => void
    switchTenant: (tenantId: string) => void
    refreshTenants: () => Promise<void>
}

const TenantContext = createContext<TenantContextType | undefined>(undefined)

// Mock tenants for demo - in production these would come from API
const mockTenants: Tenant[] = [
    { id: 'demo', name: 'Demo Organization', securityScore: 72.5, status: 'warning' },
    { id: 'acme-corp', name: 'Acme Corporation', securityScore: 85.2, status: 'healthy' },
    { id: 'globex', name: 'Globex Industries', securityScore: 58.1, status: 'critical' },
    { id: 'initech', name: 'Initech Solutions', securityScore: 91.0, status: 'healthy' },
    { id: 'umbrella', name: 'Umbrella Corp', securityScore: 67.3, status: 'warning' },
]

interface TenantProviderProps {
    children: ReactNode
    initialTenantId?: string
}

export function TenantProvider({ children, initialTenantId = 'demo' }: TenantProviderProps) {
    const router = useRouter()
    const [tenants, setTenants] = useState<Tenant[]>(mockTenants)
    const [currentTenant, setCurrentTenantState] = useState<Tenant | null>(
        mockTenants.find(t => t.id === initialTenantId) || mockTenants[0]
    )
    const [isLoading, setIsLoading] = useState(false)

    const setCurrentTenant = useCallback((tenant: Tenant) => {
        setCurrentTenantState(tenant)
    }, [])

    const switchTenant = useCallback((tenantId: string) => {
        const tenant = tenants.find(t => t.id === tenantId)
        if (tenant) {
            setCurrentTenantState(tenant)
            // Navigate to the new tenant's dashboard
            router.push(`/${tenantId}/executive`)
        }
    }, [tenants, router])

    const refreshTenants = useCallback(async () => {
        setIsLoading(true)
        try {
            // In production: const response = await apiClient.listTenants()
            // For demo, just use mock data
            await new Promise(resolve => setTimeout(resolve, 500))
            setTenants(mockTenants)
        } finally {
            setIsLoading(false)
        }
    }, [])

    return (
        <TenantContext.Provider
            value={{
                currentTenant,
                tenants,
                isLoading,
                setCurrentTenant,
                switchTenant,
                refreshTenants,
            }}
        >
            {children}
        </TenantContext.Provider>
    )
}

export function useTenant() {
    const context = useContext(TenantContext)
    if (context === undefined) {
        throw new Error('useTenant must be used within a TenantProvider')
    }
    return context
}

// Default export for convenience
export default TenantContext
