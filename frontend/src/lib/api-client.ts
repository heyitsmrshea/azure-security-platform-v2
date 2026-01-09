import { ExecutiveDashboard } from '@/types/dashboard'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  setToken(token: string | null) {
    this.token = token
  }

  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
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

  // IT Staff Dashboard
  async getAlerts(tenantId: string, options?: { severity?: string; status?: string; page?: number }) {
    const params = new URLSearchParams()
    if (options?.severity) params.append('severity', options.severity)
    if (options?.status) params.append('status', options.status)
    if (options?.page) params.append('page', options.page.toString())
    return this.fetch(`/${tenantId}/it-staff/alerts?${params}`)
  }

  async getVulnerabilities(tenantId: string, options?: { severity?: string; page?: number }) {
    const params = new URLSearchParams()
    if (options?.severity) params.append('severity', options.severity)
    if (options?.page) params.append('page', options.page.toString())
    return this.fetch(`/${tenantId}/it-staff/vulnerabilities?${params}`)
  }

  async getMFAGaps(tenantId: string) {
    return this.fetch(`/${tenantId}/it-staff/mfa-gaps`)
  }

  async getPrivilegedUsers(tenantId: string) {
    return this.fetch(`/${tenantId}/it-staff/privileged-users`)
  }

  async getNonCompliantDevices(tenantId: string) {
    return this.fetch(`/${tenantId}/it-staff/non-compliant-devices`)
  }

  async getGuestUsers(tenantId: string) {
    return this.fetch(`/${tenantId}/it-staff/guest-users`)
  }

  async getThirdPartyApps(tenantId: string) {
    return this.fetch(`/${tenantId}/it-staff/third-party-apps`)
  }

  async getBackupJobs(tenantId: string, days: number = 7) {
    return this.fetch(`/${tenantId}/it-staff/backup-jobs?days=${days}`)
  }

  async getAuditLogs(tenantId: string, options?: { category?: string; days?: number }) {
    const params = new URLSearchParams()
    if (options?.category) params.append('category', options.category)
    if (options?.days) params.append('days', options.days.toString())
    return this.fetch(`/${tenantId}/it-staff/audit-logs?${params}`)
  }

  // Tenants
  async listTenants() {
    return this.fetch('/tenants/')
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
