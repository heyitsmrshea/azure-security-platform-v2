
import { ExecutiveDashboard } from '@/types/dashboard'

export const mockTenants = [
    { id: 'demo', name: 'Demo Organization', securityScore: 72.5, status: 'warning' },
    { id: 'acme-corp', name: 'Acme Corporation', securityScore: 85.2, status: 'healthy' },
    { id: 'globex', name: 'Globex Industries', securityScore: 58.1, status: 'critical' },
    { id: 'initech', name: 'Initech Solutions', securityScore: 91.0, status: 'healthy' },
]

export const mockExecutiveDashboard: ExecutiveDashboard = {
    tenant_id: 'demo',
    tenant_name: 'Demo Organization',
    security_score: {
        current_score: 72.5,
        max_score: 100,
        score_percent: 72.5,
        percentile: 65,
        trend: { direction: 'up', change_value: 3.2, change_percent: 4.6, period: '7d' },
        comparison_label: 'Top 35%',
        last_updated: new Date().toISOString(),
    },
    compliance_score: {
        framework: 'CIS Azure 2.0',
        score_percent: 68.5,
        controls_passed: 137,
        controls_total: 200,
        trend: { direction: 'up', change_value: 2.1, change_percent: 3.2, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    risk_summary: {
        critical_count: 3,
        high_count: 12,
        medium_count: 45,
        low_count: 89,
        trend: { direction: 'down', change_value: 2, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    backup_health: {
        protected_percent: 94.5,
        total_protected_items: 47,
        total_critical_systems: 50,
        last_successful_backup: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        hours_since_backup: 4,
        status: 'healthy',
        last_updated: new Date().toISOString(),
    },
    recovery_readiness: {
        rto_status: 'healthy',
        rpo_status: 'healthy',
        rto_target_hours: 24,
        rpo_target_hours: 4,
        rto_actual_hours: 18,
        rpo_actual_hours: 4,
        overall_status: 'healthy',
        last_updated: new Date().toISOString(),
    },
    mfa_coverage: {
        admin_coverage_percent: 100,
        user_coverage_percent: 87.3,
        total_admins: 8,
        admins_with_mfa: 8,
        total_users: 150,
        users_with_mfa: 131,
        trend: { direction: 'up', change_value: 2.5, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    privileged_accounts: {
        global_admin_count: 3,
        privileged_role_count: 12,
        pim_eligible_count: 8,
        pim_active_count: 2,
        trend: { direction: 'stable', change_value: 0, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    risky_users: {
        high_risk_count: 0,
        medium_risk_count: 2,
        low_risk_count: 5,
        requires_investigation: 2,
        trend: { direction: 'down', change_value: 1, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    alert_summary: {
        critical_count: 0,
        high_count: 2,
        medium_count: 8,
        low_count: 15,
        total_active: 25,
        last_updated: new Date().toISOString(),
    },
    blocked_threats: {
        phishing_blocked: 156,
        malware_blocked: 23,
        spam_blocked: 1247,
        total_blocked: 1426,
        period: '30d',
        last_updated: new Date().toISOString(),
    },
    device_compliance: {
        compliant_count: 142,
        non_compliant_count: 8,
        unknown_count: 3,
        total_devices: 153,
        compliance_percent: 92.8,
        trend: { direction: 'up', change_value: 1.2, period: '7d' },
        last_updated: new Date().toISOString(),
    },
    patch_sla: {
        compliance_percent: 89.5,
        target_percent: 95,
        patches_in_sla: 179,
        patches_total: 200,
        critical_sla_days: 7,
        high_sla_days: 14,
        medium_sla_days: 30,
        last_updated: new Date().toISOString(),
    },
    finding_age: {
        age_0_7: 15,
        age_7_30: 28,
        age_30_90: 12,
        age_90_plus: 5,
        total_open: 60,
        last_updated: new Date().toISOString(),
    },
    mttr: {
        mttr_days: 8.5,
        critical_mttr_days: 2.1,
        high_mttr_days: 5.3,
        findings_resolved_count: 45,
        period: '30d',
        last_updated: new Date().toISOString(),
    },
    score_trend: [
        { date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 58.2, compliance_score: 52.1 },
        { date: new Date(Date.now() - 150 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 61.5, compliance_score: 55.8 },
        { date: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 64.8, compliance_score: 59.2 },
        { date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 67.2, compliance_score: 62.5 },
        { date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 69.5, compliance_score: 65.1 },
        { date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), secure_score: 71.2, compliance_score: 67.3 },
        { date: new Date().toISOString(), secure_score: 72.5, compliance_score: 68.5 },
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

export const mockComplianceFrameworks = [
    { id: 'soc2', name: 'SOC 2 Type II', lookup: 'SOC 2', version: '2017', compliance_percent: 85.0, total: 10, passing: 7, failing: 1, partial: 2 },
    { id: 'iso27001', name: 'ISO/IEC 27001', lookup: 'ISO 27001', version: '2022', compliance_percent: 80.0, total: 8, passing: 6, failing: 0, partial: 2 },
    { id: 'cis', name: 'CIS Azure Benchmark', lookup: 'CIS', version: '2.0', compliance_percent: 75.0, total: 6, passing: 4, failing: 1, partial: 1 },
    { id: 'pci', name: 'PCI DSS', lookup: 'PCI-DSS', version: '4.0', compliance_percent: 100.0, total: 3, passing: 3, failing: 0, partial: 0 },
]

export const mockComplianceControls = [
    { id: 'AC-001', title: 'Multi-Factor Authentication Required', status: 'partial', category: 'Access Control', frameworks: ['SOC 2', 'ISO 27001', 'CIS'] },
    { id: 'AC-002', title: 'Privileged Access Management', status: 'pass', category: 'Access Control', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'AC-003', title: 'Conditional Access Policies', status: 'pass', category: 'Access Control', frameworks: ['SOC 2', 'CIS'] },
    { id: 'DP-001', title: 'Data Encryption at Rest', status: 'pass', category: 'Data Protection', frameworks: ['SOC 2', 'ISO 27001', 'PCI-DSS'] },
    { id: 'DP-002', title: 'Data Encryption in Transit', status: 'pass', category: 'Data Protection', frameworks: ['SOC 2', 'ISO 27001', 'PCI-DSS'] },
    { id: 'BC-001', title: 'Backup Frequency', status: 'pass', category: 'Business Continuity', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'BC-002', title: 'Backup Testing', status: 'partial', category: 'Business Continuity', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'IR-001', title: 'Incident Response Plan', status: 'pass', category: 'Incident Response', frameworks: ['SOC 2', 'ISO 27001', 'NIST'] },
    { id: 'VM-001', title: 'Vulnerability Scanning', status: 'pass', category: 'Vulnerability Mgmt', frameworks: ['SOC 2', 'CIS', 'PCI-DSS'] },
    { id: 'VM-002', title: 'Patch Management SLA', status: 'fail', category: 'Vulnerability Mgmt', frameworks: ['SOC 2', 'CIS'] },
]

export const mockAlerts = [
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

export const mockVulnerabilities = [
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

export const mockMFAGaps = [
    { user_id: 'user-001', display_name: 'Jane Smith', email: 'jane.smith@company.com', department: 'Marketing', is_admin: false, last_sign_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
    { user_id: 'user-002', display_name: 'Bob Wilson', email: 'bob.wilson@company.com', department: 'Sales', is_admin: false, last_sign_in: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
    { user_id: 'user-003', display_name: 'Alice Brown', email: 'alice.brown@company.com', department: 'Engineering', is_admin: false, last_sign_in: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() },
]

export const mockPrivilegedUsers = [
    { user_id: 'admin-001', display_name: 'IT Admin', email: 'it.admin@company.com', roles: ['Global Administrator'], is_pim_eligible: false, is_pim_active: true, last_activity: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
    { user_id: 'admin-002', display_name: 'Security Admin', email: 'security.admin@company.com', roles: ['Security Administrator', 'Compliance Administrator'], is_pim_eligible: true, is_pim_active: false, last_activity: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
    { user_id: 'admin-003', display_name: 'User Admin', email: 'user.admin@company.com', roles: ['User Administrator'], is_pim_eligible: true, is_pim_active: true, last_activity: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), mfa_enabled: true },
]

export const mockNonCompliantDevices = [
    { device_id: 'device-001', device_name: 'LAPTOP-XYZ789', os_type: 'Windows', os_version: '10.0.19044', owner: 'john.doe@company.com', compliance_state: 'noncompliant', failure_reasons: ['Firewall disabled', 'Antivirus out of date'], last_check_in: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
    { device_id: 'device-002', device_name: 'DESKTOP-ABC456', os_type: 'Windows', os_version: '10.0.19041', owner: 'jane.smith@company.com', compliance_state: 'noncompliant', failure_reasons: ['OS version outdated'], last_check_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
]

export const mockGuestUsers = [
    { user_id: 'guest-001', display_name: 'External Consultant', email: 'consultant@partner.com', source: 'Invited', created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(), last_sign_in: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), access_level: 'Member of 3 Teams' },
    { user_id: 'guest-002', display_name: 'Vendor Contact', email: 'support@vendor.com', source: 'B2B', created_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), last_sign_in: new Date(Date.now() - 95 * 24 * 60 * 60 * 1000).toISOString(), access_level: 'SharePoint site access' },
]

export const mockThirdPartyApps = [
    { app_id: 'app-001', display_name: 'Slack', publisher: 'Slack Technologies', permissions: ['User.Read', 'Calendars.Read'], consent_type: 'admin', consented_by: 'IT Admin', consented_at: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString() },
    { app_id: 'app-002', display_name: 'Zoom', publisher: 'Zoom Video Communications', permissions: ['User.Read', 'OnlineMeetings.ReadWrite'], consent_type: 'admin', consented_by: 'IT Admin', consented_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
    { app_id: 'app-003', display_name: 'Unknown App', publisher: 'Unknown Publisher', permissions: ['Mail.Read', 'Files.ReadWrite.All'], consent_type: 'user', consented_by: 'john.doe@company.com', consented_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() },
]

export const mockBackupJobs = [
    { job_id: 'job-001', protected_item: 'SQL-SERVER-01', vault_name: 'prod-backup-vault', status: 'Completed', start_time: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), duration_minutes: 15 },
    { job_id: 'job-002', protected_item: 'FILE-SERVER-01', vault_name: 'prod-backup-vault', status: 'Completed', start_time: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), duration_minutes: 30 },
    { job_id: 'job-003', protected_item: 'WEB-SERVER-01', vault_name: 'prod-backup-vault', status: 'Failed', start_time: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), duration_minutes: 5, error_message: 'Insufficient disk space on backup target' },
]

export const mockAuditLogs = [
    { id: 'audit-001', activity: 'Add member to role', category: 'RoleManagement', initiated_by: 'IT Admin', target_resource: 'User: john.doe@company.com', result: 'success', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
    { id: 'audit-002', activity: 'Update conditional access policy', category: 'Policy', initiated_by: 'Security Admin', target_resource: 'Policy: Require MFA for admins', result: 'success', timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString() },
    { id: 'audit-003', activity: 'Delete user', category: 'UserManagement', initiated_by: 'HR System', target_resource: 'User: former.employee@company.com', result: 'success', timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString() },
]

export const mockHighRiskOps = [
    { operation: 'Global Admin role assigned', initiated_by: 'IT Admin', target: 'new.admin@company.com', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), risk_reason: 'Highly privileged role assignment' },
    { operation: 'Conditional Access policy disabled', initiated_by: 'Security Admin', target: 'Block legacy auth policy', timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), risk_reason: 'Security control disabled' },
]
