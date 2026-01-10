export interface Alert {
    id: string
    title: string
    description: string
    severity: 'critical' | 'high' | 'medium' | 'low'
    status: 'active' | 'resolved' | 'investigating'
    category: string
    resource_name: string
    resource_type: string
    created_at: string
}

export interface Vulnerability {
    id: string
    cve_id: string
    title: string
    description: string
    severity: 'critical' | 'high' | 'medium' | 'low'
    cvss_score: number
    affected_resource: string
    resource_type: string
    first_seen: string
    status: 'open' | 'in_progress' | 'resolved'
    remediation: string
}

export interface MFAGap {
    user_id: string
    display_name: string
    email: string
    department: string
    is_admin: boolean
    last_sign_in: string
}

export interface PrivilegedUser {
    user_id: string
    display_name: string
    email: string
    roles: string[]
    is_pim_eligible: boolean
    is_pim_active: boolean
    last_activity: string
    mfa_enabled: boolean
}

export interface Device {
    device_id: string
    device_name: string
    os_type: string
    os_version: string
    owner: string
    compliance_state: 'compliant' | 'noncompliant'
    failure_reasons: string[]
    last_check_in: string
}

export interface GuestUser {
    user_id: string
    display_name: string
    email: string
    source: string
    created_at: string
    last_sign_in: string
    access_level: string
}

export interface ThirdPartyApp {
    app_id: string
    display_name: string
    publisher: string
    permissions: string[]
    consent_type: 'admin' | 'user'
    consented_by: string
    consented_at: string
}

export interface BackupJob {
    job_id: string
    protected_item: string
    vault_name: string
    status: 'Completed' | 'Failed' | 'In Progress'
    start_time: string
    duration_minutes: number
    error_message?: string
}

export interface AuditLog {
    id: string
    activity: string
    category: string
    initiated_by: string
    target_resource: string
    result: 'success' | 'failure'
    timestamp: string
    details?: Record<string, any>
}

export interface HighRiskOperation {
    operation: string
    initiated_by: string
    target: string
    timestamp: string
    risk_reason: string
}
