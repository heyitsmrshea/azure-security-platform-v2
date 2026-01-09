'use client'

import { useState } from 'react'
import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { StatusBadge, SeverityBadge } from '@/components/shared/StatusBadge'
import { AlertQueue } from '@/components/it-staff/AlertQueue'
import { VulnerabilityView } from '@/components/it-staff/VulnerabilityView'
import { AuditTrail, HighRiskOperations } from '@/components/it-staff/AuditTrail'
import { DataTable } from '@/components/it-staff/DataTable'
import { cn, getTimeAgo } from '@/lib/utils'
import {
  Bell,
  ShieldAlert,
  Users,
  Shield,
  UserX,
  Laptop,
  UserPlus,
  AppWindow,
  Share2,
  HardDrive,
  FileText,
  AlertTriangle,
} from 'lucide-react'

// Mock data
const mockAlerts = [
  {
    id: 'alert-001',
    title: 'Suspicious sign-in activity detected',
    description: 'Multiple failed sign-in attempts followed by successful login from unusual location',
    severity: 'high',
    status: 'active',
    category: 'Identity',
    resource_name: 'john.doe@company.com',
    resource_type: 'User',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'alert-002',
    title: 'Malware detected on device',
    description: 'Windows Defender detected and quarantined malicious file',
    severity: 'medium',
    status: 'resolved',
    category: 'Endpoint',
    resource_name: 'DESKTOP-ABC123',
    resource_type: 'Device',
    created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'alert-003',
    title: 'Unusual resource access pattern',
    description: 'User accessed 50+ files in SharePoint within 5 minutes',
    severity: 'medium',
    status: 'investigating',
    category: 'Data',
    resource_name: 'Marketing Documents',
    resource_type: 'SharePoint Site',
    created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
  },
]

const mockVulnerabilities = [
  {
    id: 'vuln-001',
    cve_id: 'CVE-2024-1234',
    title: 'Remote Code Execution in Windows Server',
    description: 'A remote code execution vulnerability exists in Windows Server',
    severity: 'critical',
    cvss_score: 9.8,
    affected_resource: 'SQL-SERVER-01',
    resource_type: 'Virtual Machine',
    first_seen: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'open',
    remediation: 'Apply KB5001234 security update',
  },
  {
    id: 'vuln-002',
    cve_id: 'CVE-2024-5678',
    title: 'Privilege Escalation in Azure AD Connect',
    description: 'Local privilege escalation vulnerability in AD Connect sync service',
    severity: 'high',
    cvss_score: 7.8,
    affected_resource: 'ADCONNECT-01',
    resource_type: 'Server',
    first_seen: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'in_progress',
    remediation: 'Upgrade to AD Connect version 2.1.x',
  },
  {
    id: 'vuln-003',
    cve_id: 'CVE-2024-9012',
    title: 'Information Disclosure in IIS',
    description: 'IIS may disclose sensitive information in error messages',
    severity: 'medium',
    cvss_score: 5.3,
    affected_resource: 'WEB-SERVER-01',
    resource_type: 'Virtual Machine',
    first_seen: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'open',
    remediation: 'Configure custom error pages',
  },
]

const mockMFAGaps = [
  { user_id: 'user-001', display_name: 'Jane Smith', email: 'jane.smith@company.com', department: 'Marketing', is_admin: false, last_sign_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
  { user_id: 'user-002', display_name: 'Bob Wilson', email: 'bob.wilson@company.com', department: 'Sales', is_admin: false, last_sign_in: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
  { user_id: 'user-003', display_name: 'Alice Brown', email: 'alice.brown@company.com', department: 'Engineering', is_admin: false, last_sign_in: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() },
]

const mockPrivilegedUsers = [
  { user_id: 'admin-001', display_name: 'IT Admin', email: 'it.admin@company.com', roles: ['Global Administrator'], is_pim_eligible: false, is_pim_active: true, last_activity: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
  { user_id: 'admin-002', display_name: 'Security Admin', email: 'security.admin@company.com', roles: ['Security Administrator', 'Compliance Administrator'], is_pim_eligible: true, is_pim_active: false, last_activity: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
  { user_id: 'admin-003', display_name: 'User Admin', email: 'user.admin@company.com', roles: ['User Administrator'], is_pim_eligible: true, is_pim_active: true, last_activity: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
]

const mockNonCompliantDevices = [
  { device_id: 'device-001', device_name: 'LAPTOP-XYZ789', os_type: 'Windows', os_version: '10.0.19044', owner: 'john.doe@company.com', compliance_state: 'noncompliant', failure_reasons: ['Firewall disabled', 'Antivirus out of date'], last_check_in: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { device_id: 'device-002', device_name: 'DESKTOP-ABC456', os_type: 'Windows', os_version: '10.0.19041', owner: 'jane.smith@company.com', compliance_state: 'noncompliant', failure_reasons: ['OS version outdated'], last_check_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
]

const mockGuestUsers = [
  { user_id: 'guest-001', display_name: 'External Consultant', email: 'consultant@partner.com', source: 'Invited', created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(), last_sign_in: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), access_level: 'Member of 3 Teams' },
  { user_id: 'guest-002', display_name: 'Vendor Contact', email: 'support@vendor.com', source: 'B2B', created_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), last_sign_in: new Date(Date.now() - 95 * 24 * 60 * 60 * 1000).toISOString(), access_level: 'SharePoint site access' },
]

const mockThirdPartyApps = [
  { app_id: 'app-001', display_name: 'Slack', publisher: 'Slack Technologies', permissions: ['User.Read', 'Calendars.Read'], consent_type: 'admin', consented_by: 'IT Admin', consented_at: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString() },
  { app_id: 'app-002', display_name: 'Zoom', publisher: 'Zoom Video Communications', permissions: ['User.Read', 'OnlineMeetings.ReadWrite'], consent_type: 'admin', consented_by: 'IT Admin', consented_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
  { app_id: 'app-003', display_name: 'Unknown App', publisher: 'Unknown Publisher', permissions: ['Mail.Read', 'Files.ReadWrite.All'], consent_type: 'user', consented_by: 'john.doe@company.com', consented_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() },
]

const mockBackupJobs = [
  { job_id: 'job-001', protected_item: 'SQL-SERVER-01', vault_name: 'prod-backup-vault', status: 'Completed', start_time: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), duration_minutes: 15 },
  { job_id: 'job-002', protected_item: 'FILE-SERVER-01', vault_name: 'prod-backup-vault', status: 'Completed', start_time: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), duration_minutes: 30 },
  { job_id: 'job-003', protected_item: 'WEB-SERVER-01', vault_name: 'prod-backup-vault', status: 'Failed', start_time: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), duration_minutes: 5, error_message: 'Insufficient disk space on backup target' },
]

const mockAuditLogs = [
  { id: 'audit-001', activity: 'Add member to role', category: 'RoleManagement', initiated_by: 'IT Admin', target_resource: 'User: john.doe@company.com', result: 'success', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: 'audit-002', activity: 'Update conditional access policy', category: 'Policy', initiated_by: 'Security Admin', target_resource: 'Policy: Require MFA for admins', result: 'success', timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString() },
  { id: 'audit-003', activity: 'Delete user', category: 'UserManagement', initiated_by: 'HR System', target_resource: 'User: former.employee@company.com', result: 'success', timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString() },
]

const mockHighRiskOps = [
  { operation: 'Global Admin role assigned', initiated_by: 'IT Admin', target: 'new.admin@company.com', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), risk_reason: 'Highly privileged role assignment' },
  { operation: 'Conditional Access policy disabled', initiated_by: 'Security Admin', target: 'Block legacy auth policy', timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), risk_reason: 'Security control disabled' },
]

type TabId = 'alerts' | 'vulnerabilities' | 'identity' | 'devices' | 'vendor' | 'backup' | 'audit'

export default function ITStaffDashboardPage({
  params,
}: {
  params: { tenantId: string }
}) {
  const [activeTab, setActiveTab] = useState<TabId>('alerts')

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'alerts', label: 'Alerts & Incidents', icon: <Bell className="w-4 h-4" /> },
    { id: 'vulnerabilities', label: 'Vulnerabilities', icon: <ShieldAlert className="w-4 h-4" /> },
    { id: 'identity', label: 'Identity & Access', icon: <Users className="w-4 h-4" /> },
    { id: 'devices', label: 'Device Security', icon: <Laptop className="w-4 h-4" /> },
    { id: 'vendor', label: 'Third-Party Risk', icon: <AppWindow className="w-4 h-4" /> },
    { id: 'backup', label: 'Backup & Recovery', icon: <HardDrive className="w-4 h-4" /> },
    { id: 'audit', label: 'Audit Trail', icon: <FileText className="w-4 h-4" /> },
  ]

  return (
    <div className="min-h-screen bg-background-primary">
      <DashboardHeader
        tenantName="Demo Organization"
        title="IT Staff Dashboard"
        minutesAgo={5}
        onRefresh={() => console.log('Refresh')}
      />

      <main className="p-6">
        {/* Tab Navigation */}
        <div className="flex items-center gap-1 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
                activeTab === tab.id
                  ? 'bg-accent text-foreground-primary'
                  : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'alerts' && (
            <AlertQueue alerts={mockAlerts} />
          )}

          {activeTab === 'vulnerabilities' && (
            <VulnerabilityView vulnerabilities={mockVulnerabilities} />
          )}

          {activeTab === 'identity' && (
            <div className="space-y-6">
              {/* MFA Gaps */}
              <div className="card">
                <h3 className="section-title flex items-center gap-2 mb-4">
                  <Shield className="w-5 h-5 text-status-warning" />
                  Users Without MFA
                </h3>
                <DataTable
                  data={mockMFAGaps}
                  columns={[
                    { key: 'display_name', header: 'Name', sortable: true },
                    { key: 'email', header: 'Email', sortable: true },
                    { key: 'department', header: 'Department', sortable: true },
                    {
                      key: 'is_admin',
                      header: 'Admin',
                      render: (user) => user.is_admin ? (
                        <span className="text-severity-high">Yes</span>
                      ) : <span className="text-foreground-muted">No</span>
                    },
                    {
                      key: 'last_sign_in',
                      header: 'Last Sign-in',
                      sortable: true,
                      render: (user) => <span className="text-foreground-muted">{getTimeAgo(user.last_sign_in)}</span>
                    },
                  ]}
                  searchKeys={['display_name', 'email', 'department']}
                />
              </div>

              {/* Privileged Users */}
              <div className="card">
                <h3 className="section-title flex items-center gap-2 mb-4">
                  <UserX className="w-5 h-5 text-accent" />
                  Privileged Access Inventory
                </h3>
                <DataTable
                  data={mockPrivilegedUsers}
                  columns={[
                    { key: 'display_name', header: 'Name', sortable: true },
                    { key: 'email', header: 'Email', sortable: true },
                    {
                      key: 'roles',
                      header: 'Roles',
                      render: (user) => (
                        <div className="flex flex-wrap gap-1">
                          {user.roles.map((role: string, i: number) => (
                            <span key={i} className="px-2 py-0.5 bg-accent/20 text-accent text-xs rounded">
                              {role}
                            </span>
                          ))}
                        </div>
                      )
                    },
                    {
                      key: 'is_pim_eligible',
                      header: 'PIM Status',
                      render: (user) => (
                        <span className={cn(
                          'px-2 py-1 rounded text-xs',
                          user.is_pim_eligible ? 'bg-status-success/20 text-status-success' : 'bg-status-warning/20 text-status-warning'
                        )}>
                          {user.is_pim_eligible ? 'Eligible' : 'Permanent'}
                        </span>
                      )
                    },
                    {
                      key: 'mfa_enabled',
                      header: 'MFA',
                      render: (user) => (
                        <StatusBadge status={user.mfa_enabled ? 'healthy' : 'critical'} label={user.mfa_enabled ? 'Enabled' : 'Disabled'} size="sm" />
                      )
                    },
                    {
                      key: 'last_activity',
                      header: 'Last Activity',
                      sortable: true,
                      render: (user) => <span className="text-foreground-muted">{getTimeAgo(user.last_activity)}</span>
                    },
                  ]}
                  searchKeys={['display_name', 'email']}
                />
              </div>
            </div>
          )}

          {activeTab === 'devices' && (
            <div className="card">
              <h3 className="section-title flex items-center gap-2 mb-4">
                <Laptop className="w-5 h-5 text-severity-high" />
                Non-Compliant Devices
              </h3>
              <DataTable
                data={mockNonCompliantDevices}
                columns={[
                  { key: 'device_name', header: 'Device', sortable: true },
                  {
                    key: 'os_type',
                    header: 'OS',
                    render: (device) => (
                      <span>{device.os_type} {device.os_version}</span>
                    )
                  },
                  { key: 'owner', header: 'Owner', sortable: true },
                  {
                    key: 'failure_reasons',
                    header: 'Issues',
                    render: (device) => (
                      <div className="flex flex-wrap gap-1">
                        {device.failure_reasons.map((reason: string, i: number) => (
                          <span key={i} className="px-2 py-0.5 bg-severity-high/20 text-severity-high text-xs rounded">
                            {reason}
                          </span>
                        ))}
                      </div>
                    )
                  },
                  {
                    key: 'last_check_in',
                    header: 'Last Check-in',
                    sortable: true,
                    render: (device) => <span className="text-foreground-muted">{getTimeAgo(device.last_check_in)}</span>
                  },
                ]}
                searchKeys={['device_name', 'owner']}
              />
            </div>
          )}

          {activeTab === 'vendor' && (
            <div className="space-y-6">
              {/* Guest Users */}
              <div className="card">
                <h3 className="section-title flex items-center gap-2 mb-4">
                  <UserPlus className="w-5 h-5 text-accent" />
                  Guest User Inventory
                </h3>
                <DataTable
                  data={mockGuestUsers}
                  columns={[
                    { key: 'display_name', header: 'Name', sortable: true },
                    { key: 'email', header: 'Email', sortable: true },
                    { key: 'source', header: 'Source', sortable: true },
                    { key: 'access_level', header: 'Access Level' },
                    {
                      key: 'last_sign_in',
                      header: 'Last Sign-in',
                      sortable: true,
                      render: (user) => {
                        const days = Math.floor((Date.now() - new Date(user.last_sign_in).getTime()) / (1000 * 60 * 60 * 24))
                        return (
                          <span className={cn(
                            days > 90 ? 'text-severity-high' : 'text-foreground-muted'
                          )}>
                            {getTimeAgo(user.last_sign_in)}
                            {days > 90 && ' (Stale)'}
                          </span>
                        )
                      }
                    },
                  ]}
                  searchKeys={['display_name', 'email']}
                />
              </div>

              {/* Third-Party Apps */}
              <div className="card">
                <h3 className="section-title flex items-center gap-2 mb-4">
                  <AppWindow className="w-5 h-5 text-accent" />
                  Third-Party App Permissions
                </h3>
                <DataTable
                  data={mockThirdPartyApps}
                  columns={[
                    { key: 'display_name', header: 'App', sortable: true },
                    { key: 'publisher', header: 'Publisher', sortable: true },
                    {
                      key: 'permissions',
                      header: 'Permissions',
                      render: (app) => (
                        <div className="flex flex-wrap gap-1">
                          {app.permissions.slice(0, 3).map((perm: string, i: number) => (
                            <span key={i} className={cn(
                              'px-2 py-0.5 text-xs rounded',
                              perm.includes('Write') || perm.includes('All')
                                ? 'bg-severity-high/20 text-severity-high'
                                : 'bg-background-tertiary text-foreground-secondary'
                            )}>
                              {perm}
                            </span>
                          ))}
                          {app.permissions.length > 3 && (
                            <span className="text-xs text-foreground-muted">+{app.permissions.length - 3} more</span>
                          )}
                        </div>
                      )
                    },
                    {
                      key: 'consent_type',
                      header: 'Consent',
                      render: (app) => (
                        <span className={cn(
                          'px-2 py-1 rounded text-xs capitalize',
                          app.consent_type === 'admin' ? 'bg-status-success/20 text-status-success' : 'bg-status-warning/20 text-status-warning'
                        )}>
                          {app.consent_type}
                        </span>
                      )
                    },
                    { key: 'consented_by', header: 'Consented By' },
                  ]}
                  searchKeys={['display_name', 'publisher']}
                />
              </div>
            </div>
          )}

          {activeTab === 'backup' && (
            <div className="card">
              <h3 className="section-title flex items-center gap-2 mb-4">
                <HardDrive className="w-5 h-5 text-accent" />
                Backup Job Status
              </h3>
              <DataTable
                data={mockBackupJobs}
                columns={[
                  { key: 'protected_item', header: 'Protected Item', sortable: true },
                  { key: 'vault_name', header: 'Vault', sortable: true },
                  {
                    key: 'status',
                    header: 'Status',
                    sortable: true,
                    render: (job) => (
                      <StatusBadge
                        status={job.status === 'Completed' ? 'healthy' : job.status === 'Failed' ? 'critical' : 'warning'}
                        label={job.status}
                        size="sm"
                      />
                    )
                  },
                  {
                    key: 'start_time',
                    header: 'Started',
                    sortable: true,
                    render: (job) => <span className="text-foreground-muted">{getTimeAgo(job.start_time)}</span>
                  },
                  {
                    key: 'duration_minutes',
                    header: 'Duration',
                    render: (job) => <span>{job.duration_minutes} min</span>
                  },
                  {
                    key: 'error_message',
                    header: 'Error',
                    render: (job) => job.error_message ? (
                      <span className="text-severity-high text-sm">{job.error_message}</span>
                    ) : '-'
                  },
                ]}
                searchKeys={['protected_item', 'vault_name']}
              />
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AuditTrail logs={mockAuditLogs} />
              <HighRiskOperations operations={mockHighRiskOps} />
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
