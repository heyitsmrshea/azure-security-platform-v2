import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

// Query keys for consistent caching
export const queryKeys = {
  // Executive Dashboard
  executiveDashboard: (tenantId: string) => ['executive', 'dashboard', tenantId] as const,
  securityScore: (tenantId: string) => ['executive', 'security-score', tenantId] as const,
  complianceScore: (tenantId: string, framework?: string) => ['executive', 'compliance-score', tenantId, framework] as const,
  backupHealth: (tenantId: string) => ['executive', 'backup-health', tenantId] as const,
  scoreTrend: (tenantId: string) => ['executive', 'score-trend', tenantId] as const,
  topRisks: (tenantId: string) => ['executive', 'top-risks', tenantId] as const,

  // IT Staff Dashboard
  alerts: (tenantId: string, filters?: Record<string, string>) => ['it-staff', 'alerts', tenantId, filters] as const,
  vulnerabilities: (tenantId: string, filters?: Record<string, string>) => ['it-staff', 'vulnerabilities', tenantId, filters] as const,
  mfaGaps: (tenantId: string) => ['it-staff', 'mfa-gaps', tenantId] as const,
  privilegedUsers: (tenantId: string) => ['it-staff', 'privileged-users', tenantId] as const,
  nonCompliantDevices: (tenantId: string) => ['it-staff', 'non-compliant-devices', tenantId] as const,
  guestUsers: (tenantId: string) => ['it-staff', 'guest-users', tenantId] as const,
  thirdPartyApps: (tenantId: string) => ['it-staff', 'third-party-apps', tenantId] as const,
  backupJobs: (tenantId: string) => ['it-staff', 'backup-jobs', tenantId] as const,
  auditLogs: (tenantId: string, filters?: Record<string, string>) => ['it-staff', 'audit-logs', tenantId, filters] as const,

  // Tenants
  tenants: () => ['tenants'] as const,
  tenant: (tenantId: string) => ['tenants', tenantId] as const,
}
