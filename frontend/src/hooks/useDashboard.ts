'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { queryKeys } from '@/lib/query-client'
import { ExecutiveDashboard } from '@/types/dashboard'

// Mock data for demo mode
const createMockDashboard = (tenantId: string): ExecutiveDashboard => {
  const now = new Date()
  return {
    tenant_id: tenantId,
    tenant_name: 'Demo Organization',
    security_score: {
      current_score: 72.5,
      max_score: 100,
      percentile: 65,
      trend: { direction: 'up', change_value: 3.2, change_percent: 4.6, period: '7d' },
      comparison_label: 'Top 35%',
      last_updated: now.toISOString(),
    },
    compliance_score: {
      framework: 'CIS Azure 2.0',
      score_percent: 68.5,
      controls_passed: 137,
      controls_total: 200,
      trend: { direction: 'up', change_value: 2.1, change_percent: 3.2, period: '7d' },
      last_updated: now.toISOString(),
    },
    risk_summary: {
      critical_count: 3,
      high_count: 12,
      medium_count: 45,
      low_count: 89,
      trend: { direction: 'down', change_value: 2, period: '7d' },
      last_updated: now.toISOString(),
    },
    backup_health: {
      protected_percent: 94.5,
      total_protected_items: 47,
      total_critical_systems: 50,
      last_successful_backup: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      hours_since_backup: 4,
      status: 'healthy',
      last_updated: now.toISOString(),
    },
    recovery_readiness: {
      rto_status: 'healthy',
      rpo_status: 'healthy',
      rto_target_hours: 24,
      rpo_target_hours: 4,
      rto_actual_hours: 18,
      rpo_actual_hours: 4,
      overall_status: 'healthy',
      last_updated: now.toISOString(),
    },
    mfa_coverage: {
      admin_coverage_percent: 100,
      user_coverage_percent: 87.3,
      total_admins: 8,
      admins_with_mfa: 8,
      total_users: 150,
      users_with_mfa: 131,
      trend: { direction: 'up', change_value: 2.5, period: '7d' },
      last_updated: now.toISOString(),
    },
    privileged_accounts: {
      global_admin_count: 3,
      privileged_role_count: 12,
      pim_eligible_count: 8,
      pim_active_count: 2,
      trend: { direction: 'stable', change_value: 0, period: '7d' },
      last_updated: now.toISOString(),
    },
    risky_users: {
      high_risk_count: 0,
      medium_risk_count: 2,
      low_risk_count: 5,
      requires_investigation: 2,
      trend: { direction: 'down', change_value: 1, period: '7d' },
      last_updated: now.toISOString(),
    },
    alert_summary: {
      critical_count: 0,
      high_count: 2,
      medium_count: 8,
      low_count: 15,
      total_active: 25,
      last_updated: now.toISOString(),
    },
    blocked_threats: {
      phishing_blocked: 156,
      malware_blocked: 23,
      spam_blocked: 1247,
      total_blocked: 1426,
      period: '30d',
      last_updated: now.toISOString(),
    },
    device_compliance: {
      compliant_count: 142,
      non_compliant_count: 8,
      unknown_count: 3,
      total_devices: 153,
      compliance_percent: 92.8,
      trend: { direction: 'up', change_value: 1.2, period: '7d' },
      last_updated: now.toISOString(),
    },
    patch_sla: {
      compliance_percent: 89.5,
      target_percent: 95,
      patches_in_sla: 179,
      patches_total: 200,
      critical_sla_days: 7,
      high_sla_days: 14,
      medium_sla_days: 30,
      last_updated: now.toISOString(),
    },
    finding_age: {
      age_0_7: 15,
      age_7_30: 28,
      age_30_90: 12,
      age_90_plus: 5,
      total_open: 60,
      last_updated: now.toISOString(),
    },
    mttr: {
      mttr_days: 8.5,
      critical_mttr_days: 2.1,
      high_mttr_days: 5.3,
      findings_resolved_count: 45,
      period: '30d',
      last_updated: now.toISOString(),
    },
    score_trend: [
      { date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 58.2, compliance_score: 52.1 },
      { date: new Date(Date.now() - 150 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 61.5, compliance_score: 55.8 },
      { date: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 64.8, compliance_score: 59.2 },
      { date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 67.2, compliance_score: 62.5 },
      { date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 69.5, compliance_score: 65.1 },
      { date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 71.2, compliance_score: 67.3 },
      { date: now.toISOString(), secure_score: 72.5, compliance_score: 68.5 },
    ],
    top_risks: [
      {
        title: 'Legacy Authentication Enabled',
        description: '3 applications still allow legacy authentication protocols that bypass MFA',
        severity: 'high',
        affected_resources: 3,
        recommendation: 'Disable legacy authentication in Conditional Access policies',
      },
      {
        title: 'Unpatched Critical Vulnerabilities',
        description: '2 servers have critical vulnerabilities older than 7 days',
        severity: 'critical',
        affected_resources: 2,
        recommendation: 'Apply security patches immediately',
      },
      {
        title: 'Excessive Global Admin Count',
        description: '3 users have permanent Global Admin role (target: 2 or fewer)',
        severity: 'medium',
        affected_resources: 3,
        recommendation: 'Convert to PIM eligible assignments',
      },
      {
        title: 'External Sharing Without Review',
        description: "45 files shared externally haven't been reviewed in 90+ days",
        severity: 'medium',
        affected_resources: 45,
        recommendation: 'Review and revoke unnecessary external shares',
      },
      {
        title: 'Stale Guest Accounts',
        description: "12 guest accounts haven't signed in for 90+ days",
        severity: 'low',
        affected_resources: 12,
        recommendation: 'Review and disable inactive guest accounts',
      },
    ],
    data_freshness: {
      last_updated: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
      minutes_ago: 12,
      status: 'fresh',
    },
  }
}

export function useExecutiveDashboard(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.executiveDashboard(tenantId),
    queryFn: async () => {
      try {
        // Try to fetch from API
        return await apiClient.getExecutiveDashboard(tenantId)
      } catch (error) {
        // Fall back to mock data in demo mode
        console.log('Using mock data for demo mode')
        return createMockDashboard(tenantId)
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useSecurityScore(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.securityScore(tenantId),
    queryFn: () => apiClient.getSecurityScore(tenantId),
  })
}

export function useBackupHealth(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.backupHealth(tenantId),
    queryFn: () => apiClient.getBackupHealth(tenantId),
  })
}

export function useScoreTrend(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.scoreTrend(tenantId),
    queryFn: () => apiClient.getScoreTrend(tenantId),
  })
}

export function useTopRisks(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.topRisks(tenantId),
    queryFn: () => apiClient.getTopRisks(tenantId),
  })
}

// IT Staff hooks
export function useAlerts(tenantId: string, filters?: { severity?: string; status?: string }) {
  return useQuery({
    queryKey: queryKeys.alerts(tenantId, filters),
    queryFn: () => apiClient.getAlerts(tenantId, filters),
  })
}

export function useVulnerabilities(tenantId: string, filters?: { severity?: string }) {
  return useQuery({
    queryKey: queryKeys.vulnerabilities(tenantId, filters),
    queryFn: () => apiClient.getVulnerabilities(tenantId, filters),
  })
}

export function usePrivilegedUsers(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.privilegedUsers(tenantId),
    queryFn: () => apiClient.getPrivilegedUsers(tenantId),
  })
}

export function useAuditLogs(tenantId: string, filters?: { category?: string; days?: number }) {
  return useQuery({
    queryKey: queryKeys.auditLogs(tenantId, filters),
    queryFn: () => apiClient.getAuditLogs(tenantId, filters),
  })
}
