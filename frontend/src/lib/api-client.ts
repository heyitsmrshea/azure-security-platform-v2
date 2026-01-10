import { ExecutiveDashboard } from '@/types/dashboard'
import {
  Alert, Vulnerability, MFAGap, PrivilegedUser, Device,
  GuestUser, ThirdPartyApp, BackupJob, AuditLog, HighRiskOperation
} from '@/types/it-staff'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  setToken(token: string | null) {
    this.token = token
  }

  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Feature Flag: Mock Data
    if (process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true') {
      console.log(`[Mock API] Serving request for: ${endpoint}`)
      return this.getMockData(endpoint)
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      return response.json()
    } catch (error) {
      console.error(`API Request Failed: ${endpoint}`, error)
      throw error
    }
  }

  // Simple router to route endpoints to mock data functions
  private async getMockData(endpoint: string): Promise<any> {
    // Artificial delay to simulate network
    await new Promise(resolve => setTimeout(resolve, 300))

    if (endpoint.includes('/executive/dashboard')) return import('@/mocks/data').then(m => m.mockExecutiveDashboard)

    // IT Staff
    if (endpoint.includes('/it-staff/alerts')) return import('@/mocks/data').then(m => m.mockAlerts)
    if (endpoint.includes('/it-staff/vulnerabilities')) return import('@/mocks/data').then(m => m.mockVulnerabilities)
    if (endpoint.includes('/it-staff/mfa-gaps')) return import('@/mocks/data').then(m => m.mockMFAGaps)
    if (endpoint.includes('/it-staff/privileged-users')) return import('@/mocks/data').then(m => m.mockPrivilegedUsers)
    if (endpoint.includes('/it-staff/non-compliant-devices')) return import('@/mocks/data').then(m => m.mockNonCompliantDevices)
    if (endpoint.includes('/it-staff/guest-users')) return import('@/mocks/data').then(m => m.mockGuestUsers)
    if (endpoint.includes('/it-staff/third-party-apps')) return import('@/mocks/data').then(m => m.mockThirdPartyApps)
    if (endpoint.includes('/it-staff/backup-jobs')) return import('@/mocks/data').then(m => m.mockBackupJobs)
    if (endpoint.includes('/it-staff/audit-logs')) return import('@/mocks/data').then(m => m.mockAuditLogs)
    if (endpoint.includes('/it-staff/high-risk-operations')) return import('@/mocks/data').then(m => m.mockHighRiskOps)

    // Compliance
    if (endpoint.includes('/compliance/frameworks')) return import('@/mocks/data').then(m => [{
      id: "soc2",
      name: "SOC 2 Type II",
      version: "2017",
      compliance_percent: 78.5,
      passing: 12,
      failing: 2,
      partial: 1,
    }]) // Minimal mock fallback
    if (endpoint.includes('/compliance/controls')) return import('@/mocks/data').then(m => m.mockComplianceControls)
    if (endpoint.includes('/compliance/mapping')) return import('@/mocks/data').then(m => [])

    // Tenants
    if (endpoint.includes('/tenants/')) {
      // Mock get single tenant (just return basic info)
      const tenantId = endpoint.split('/tenants/')[1]
      return import('@/mocks/data').then(m => m.mockTenants.find(t => t.id === tenantId) || m.mockTenants[0])
    }
    if (endpoint.includes('/tenants')) return import('@/mocks/data').then(m => m.mockTenants)

    // Fallback for unmapped routes
    console.warn(`[Mock API] No mock data found for: ${endpoint}`)
    return {}
  }

  // Executive Dashboard
  async getExecutiveDashboard(tenantId: string): Promise<ExecutiveDashboard> {
    return this.fetch<ExecutiveDashboard>(`/${tenantId}/executive/dashboard`)
  }

  async getSecurityScore(tenantId: string) {
    return this.fetch(`/${tenantId}/executive/security-score`)
  }

  async getComplianceScore(tenantId: string, framework?: string) {
    const params = framework ? `?framework=${encodeURIComponent(framework)}` : ''
    return this.fetch(`/${tenantId}/executive/compliance-score${params}`)
  }

  async getBackupHealth(tenantId: string) {
    return this.fetch(`/${tenantId}/executive/backup-health`)
  }

  async getScoreTrend(tenantId: string, days: number = 180) {
    return this.fetch(`/${tenantId}/executive/score-trend?days=${days}`)
  }

  async getTopRisks(tenantId: string, limit: number = 5) {
    return this.fetch(`/${tenantId}/executive/top-risks?limit=${limit}`)
  }

  // Compliance
  async getComplianceFrameworks(tenantId: string) {
    return this.fetch(`/${tenantId}/compliance/frameworks`)
  }

  async getComplianceControls(tenantId: string, options?: { framework?: string; status?: string; category?: string }) {
    const params = new URLSearchParams()
    if (options?.framework) params.append('framework', options.framework)
    if (options?.status) params.append('status', options.status)
    if (options?.category) params.append('category', options.category)
    return this.fetch(`/${tenantId}/compliance/controls?${params}`)
  }

  async getControlMapping(tenantId: string) {
    return this.fetch(`/${tenantId}/compliance/mapping`)
  }

  async getControlEvidence(tenantId: string, controlId: string) {
    return this.fetch(`/${tenantId}/compliance/evidence/${controlId}`)
  }

  // IT Staff Dashboard
  async getAlerts(tenantId: string, options?: { severity?: string; status?: string; page?: number }): Promise<Alert[]> {
    const params = new URLSearchParams()
    if (options?.severity) params.append('severity', options.severity)
    if (options?.status) params.append('status', options.status)
    if (options?.page) params.append('page', options.page.toString())
    return this.fetch<Alert[]>(`/${tenantId}/it-staff/alerts?${params}`)
  }

  async getVulnerabilities(tenantId: string, options?: { severity?: string; page?: number }): Promise<Vulnerability[]> {
    const params = new URLSearchParams()
    if (options?.severity) params.append('severity', options.severity)
    if (options?.page) params.append('page', options.page.toString())
    return this.fetch<Vulnerability[]>(`/${tenantId}/it-staff/vulnerabilities?${params}`)
  }

  async getMFAGaps(tenantId: string): Promise<MFAGap[]> {
    return this.fetch<MFAGap[]>(`/${tenantId}/it-staff/mfa-gaps`)
  }

  async getPrivilegedUsers(tenantId: string): Promise<PrivilegedUser[]> {
    return this.fetch<PrivilegedUser[]>(`/${tenantId}/it-staff/privileged-users`)
  }

  async getNonCompliantDevices(tenantId: string): Promise<Device[]> {
    return this.fetch<Device[]>(`/${tenantId}/it-staff/non-compliant-devices`)
  }

  async getGuestUsers(tenantId: string): Promise<GuestUser[]> {
    return this.fetch<GuestUser[]>(`/${tenantId}/it-staff/guest-users`)
  }

  async getThirdPartyApps(tenantId: string): Promise<ThirdPartyApp[]> {
    return this.fetch<ThirdPartyApp[]>(`/${tenantId}/it-staff/third-party-apps`)
  }

  async getBackupJobs(tenantId: string, days: number = 7): Promise<BackupJob[]> {
    return this.fetch<BackupJob[]>(`/${tenantId}/it-staff/backup-jobs?days=${days}`)
  }

  async getAuditLogs(tenantId: string, options?: { category?: string; days?: number }): Promise<AuditLog[]> {
    const params = new URLSearchParams()
    if (options?.category) params.append('category', options.category)
    if (options?.days) params.append('days', options.days.toString())
    return this.fetch<AuditLog[]>(`/${tenantId}/it-staff/audit-logs?${params}`)
  }

  async getHighRiskOperations(tenantId: string): Promise<HighRiskOperation[]> {
    return this.fetch<HighRiskOperation[]>(`/${tenantId}/it-staff/high-risk-operations`)
  }

  async getDepartmentAnalytics(tenantId: string): Promise<{ mfa_by_department: any[], devices_by_department: any[] }> {
    return this.fetch(`/${tenantId}/it-staff/analytics/departments`)
  }

  // Tenants
  async listTenants() {
    return this.fetch('/tenants')
  }

  async getTenant(tenantId: string) {
    return this.fetch(`/tenants/${tenantId}`)
  }

  // Reports
  async generateReport(tenantId: string, request: {
    report_type: string
    format?: string
    date_range_days?: number
  }) {
    return this.fetch(`/${tenantId}/reports/generate`, {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getReportStatus(tenantId: string, reportId: string) {
    return this.fetch(`/${tenantId}/reports/status/${reportId}`)
  }

  // Health
  async healthCheck() {
    return this.fetch('/health')
  }
}

export const apiClient = new ApiClient()
export default apiClient
