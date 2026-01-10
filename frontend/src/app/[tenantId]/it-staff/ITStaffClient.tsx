'use client'

import { useState, useEffect, useCallback } from 'react'
import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { AlertQueue } from '@/components/it-staff/AlertQueue'
import { VulnerabilityView } from '@/components/it-staff/VulnerabilityView'
import { AuditTrail, HighRiskOperations } from '@/components/it-staff/AuditTrail'
import { DataTable } from '@/components/it-staff/DataTable'
import { DepartmentBreakdown } from '@/components/it-staff/DepartmentBreakdown'
import { OffboardingStatus, mockOffboardedUsers } from '@/components/it-staff/OffboardingStatus'
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
    HardDrive,
    FileText,
    UserMinus,
} from 'lucide-react'

import {
    Alert, Vulnerability, MFAGap, PrivilegedUser, Device,
    GuestUser, ThirdPartyApp, BackupJob, AuditLog, HighRiskOperation
} from '@/types/it-staff'

// Mock data
// Removed static imports for mock department data to use dynamic state

type TabId = 'alerts' | 'vulnerabilities' | 'identity' | 'devices' | 'vendor' | 'backup' | 'audit' | 'offboarding'

export function ITStaffClient({ tenantId }: { tenantId: string }) {
    const [activeTab, setActiveTab] = useState<TabId>('alerts')
    const [isLoading, setIsLoading] = useState(true)

    // Data State
    const [alerts, setAlerts] = useState<Alert[]>([])
    const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
    const [mfaGaps, setMfaGaps] = useState<MFAGap[]>([])
    const [privilegedUsers, setPrivilegedUsers] = useState<PrivilegedUser[]>([])
    const [nonCompliantDevices, setNonCompliantDevices] = useState<Device[]>([])
    const [guestUsers, setGuestUsers] = useState<GuestUser[]>([])
    const [thirdPartyApps, setThirdPartyApps] = useState<ThirdPartyApp[]>([])
    const [backupJobs, setBackupJobs] = useState<BackupJob[]>([])
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
    const [highRiskOps, setHighRiskOps] = useState<HighRiskOperation[]>([])

    // Department Data - typed for visualization components
    interface DepartmentMetric {
        department: string
        total: number
        compliant: number
        nonCompliant: number
        percentage: number
    }
    const [departmentMFAData, setDepartmentMFAData] = useState<DepartmentMetric[]>([])
    const [departmentDeviceData, setDepartmentDeviceData] = useState<DepartmentMetric[]>([])

    // Helper to extract items from paginated API responses
    const extractItems = <T,>(data: T[] | { items?: T[] } | null): T[] => {
        if (!data) return []
        if (Array.isArray(data)) return data
        return (data as { items?: T[] })?.items || []
    }

    const fetchData = useCallback(async () => {
        setIsLoading(true)
        try {
            const { apiClient } = await import('@/lib/api-client')

            // Fetch all data in parallel for the dashboard
            const [
                alertsData,
                vulnData,
                mfaData,
                privData,
                deviceData,
                guestData,
                appsData,
                backupData,
                auditData,
                highRiskData,
                deptAnalytics
            ] = await Promise.all([
                apiClient.getAlerts(tenantId),
                apiClient.getVulnerabilities(tenantId),
                apiClient.getMFAGaps(tenantId),
                apiClient.getPrivilegedUsers(tenantId),
                apiClient.getNonCompliantDevices(tenantId),
                apiClient.getGuestUsers(tenantId),
                apiClient.getThirdPartyApps(tenantId),
                apiClient.getBackupJobs(tenantId),
                apiClient.getAuditLogs(tenantId),
                apiClient.getHighRiskOperations(tenantId),
                apiClient.getDepartmentAnalytics(tenantId)
            ])

            setAlerts(extractItems<Alert>(alertsData))
            setVulnerabilities(extractItems<Vulnerability>(vulnData))
            setMfaGaps(extractItems<MFAGap>(mfaData))
            setPrivilegedUsers(extractItems<PrivilegedUser>(privData))
            setNonCompliantDevices(extractItems<Device>(deviceData))
            setGuestUsers(extractItems<GuestUser>(guestData))
            setThirdPartyApps(extractItems<ThirdPartyApp>(appsData))
            setBackupJobs(extractItems<BackupJob>(backupData))
            setAuditLogs(extractItems<AuditLog>(auditData))
            setHighRiskOps(extractItems<HighRiskOperation>(highRiskData))

            // Set department data
            if (deptAnalytics) {
                const analytics = deptAnalytics as { mfa_by_department?: DepartmentMetric[]; devices_by_department?: DepartmentMetric[] }
                setDepartmentMFAData(analytics.mfa_by_department || [])
                setDepartmentDeviceData(analytics.devices_by_department || [])
            }

        } catch (e) {
            console.error("Failed to fetch IT Staff data", e)
        } finally {
            setIsLoading(false)
        }
    }, [tenantId])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    const isDemo = tenantId === 'demo'
    const offboardingData = isDemo ? mockOffboardedUsers : []

    const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
        { id: 'alerts', label: 'Alerts & Incidents', icon: <Bell className="w-4 h-4" /> },
        { id: 'vulnerabilities', label: 'Vulnerabilities', icon: <ShieldAlert className="w-4 h-4" /> },
        { id: 'identity', label: 'Identity & Access', icon: <Users className="w-4 h-4" /> },
        { id: 'devices', label: 'Device Security', icon: <Laptop className="w-4 h-4" /> },
        { id: 'vendor', label: 'Third-Party Risk', icon: <AppWindow className="w-4 h-4" /> },
        { id: 'backup', label: 'Backup & Recovery', icon: <HardDrive className="w-4 h-4" /> },
        { id: 'audit', label: 'Audit Trail', icon: <FileText className="w-4 h-4" /> },
        { id: 'offboarding', label: 'Offboarding', icon: <UserMinus className="w-4 h-4" /> },
    ]

    // Loading State
    if (isLoading) {
        return (
            <div className="min-h-screen bg-background-primary flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
                    <p className="text-foreground-muted">Loading IT Staff Dashboard...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background-primary">
            <DashboardHeader
                tenantName={tenantId === 'demo' ? 'Demo Organization' : 'Polaris Consulting LLC'}
                tenantId={tenantId}
                title="IT Staff Dashboard"
                minutesAgo={5}
                onRefresh={fetchData}
                isRefreshing={isLoading}
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
                        <AlertQueue alerts={alerts} />
                    )}

                    {activeTab === 'vulnerabilities' && (
                        <VulnerabilityView vulnerabilities={vulnerabilities} />
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
                                    data={mfaGaps}
                                    columns={[
                                        { key: 'display_name', header: 'Name', sortable: true },
                                        { key: 'email', header: 'Email', sortable: true },
                                        { key: 'department', header: 'Department', sortable: true },
                                        {
                                            key: 'is_admin',
                                            header: 'Admin',
                                            render: (user: any) => user.is_admin ? (
                                                <span className="text-severity-high">Yes</span>
                                            ) : <span className="text-foreground-muted">No</span>
                                        },
                                        {
                                            key: 'last_sign_in',
                                            header: 'Last Sign-in',
                                            sortable: true,
                                            render: (user: any) => <span className="text-foreground-muted">{getTimeAgo(user.last_sign_in)}</span>
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
                                    data={privilegedUsers}
                                    columns={[
                                        { key: 'display_name', header: 'Name', sortable: true },
                                        { key: 'email', header: 'Email', sortable: true },
                                        {
                                            key: 'roles',
                                            header: 'Roles',
                                            render: (user: any) => (
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
                                            render: (user: any) => (
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
                                            render: (user: any) => (
                                                <StatusBadge status={user.mfa_enabled ? 'healthy' : 'critical'} label={user.mfa_enabled ? 'Enabled' : 'Disabled'} size="sm" />
                                            )
                                        },
                                        {
                                            key: 'last_activity',
                                            header: 'Last Activity',
                                            sortable: true,
                                            render: (user: any) => <span className="text-foreground-muted">{getTimeAgo(user.last_activity)}</span>
                                        },
                                    ]}
                                    searchKeys={['display_name', 'email']}
                                />
                            </div>

                            {/* Department Breakdowns */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <DepartmentBreakdown
                                    title="MFA Coverage by Department"
                                    data={departmentMFAData}
                                    type="mfa"
                                />
                                <DepartmentBreakdown
                                    title="Device Compliance by Department"
                                    data={departmentDeviceData}
                                    type="device"
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
                                data={nonCompliantDevices}
                                columns={[
                                    { key: 'device_name', header: 'Device', sortable: true },
                                    {
                                        key: 'os_type',
                                        header: 'OS',
                                        render: (device: any) => (
                                            <span>{device.os_type} {device.os_version}</span>
                                        )
                                    },
                                    { key: 'owner', header: 'Owner', sortable: true },
                                    {
                                        key: 'failure_reasons',
                                        header: 'Issues',
                                        render: (device: any) => (
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
                                        render: (device: any) => <span className="text-foreground-muted">{getTimeAgo(device.last_check_in)}</span>
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
                                    data={guestUsers}
                                    columns={[
                                        { key: 'display_name', header: 'Name', sortable: true },
                                        { key: 'email', header: 'Email', sortable: true },
                                        { key: 'source', header: 'Source', sortable: true },
                                        { key: 'access_level', header: 'Access Level' },
                                        {
                                            key: 'last_sign_in',
                                            header: 'Last Sign-in',
                                            sortable: true,
                                            render: (user: any) => {
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
                                    data={thirdPartyApps}
                                    columns={[
                                        { key: 'display_name', header: 'App', sortable: true },
                                        { key: 'publisher', header: 'Publisher', sortable: true },
                                        {
                                            key: 'permissions',
                                            header: 'Permissions',
                                            render: (app: any) => (
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
                                            render: (app: any) => (
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
                                data={backupJobs}
                                columns={[
                                    { key: 'protected_item', header: 'Protected Item', sortable: true },
                                    { key: 'vault_name', header: 'Vault', sortable: true },
                                    {
                                        key: 'status',
                                        header: 'Status',
                                        sortable: true,
                                        render: (job: any) => (
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
                                        render: (job: any) => <span className="text-foreground-muted">{getTimeAgo(job.start_time)}</span>
                                    },
                                    {
                                        key: 'duration_minutes',
                                        header: 'Duration',
                                        render: (job: any) => <span>{job.duration_minutes} min</span>
                                    },
                                    {
                                        key: 'error_message',
                                        header: 'Error',
                                        render: (job: any) => job.error_message ? (
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
                            <AuditTrail logs={auditLogs} />
                            <HighRiskOperations operations={highRiskOps} />
                        </div>
                    )}

                    {activeTab === 'offboarding' && (
                        <OffboardingStatus users={offboardingData} />
                    )}
                </div>
            </main>
        </div>
    )
}
