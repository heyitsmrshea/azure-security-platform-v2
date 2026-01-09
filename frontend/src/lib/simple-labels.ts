/**
 * Simple label mappings for non-technical users
 * Maps technical terminology to plain language
 */
export const simpleLabels: Record<string, string> = {
    // Security Metrics
    'Security Score': 'Overall Security Rating',
    'Compliance Score': 'Policy Compliance Rating',
    'Active Risks': 'Security Issues Found',

    // Backup & Recovery
    'Backup Health': 'Data Backup Status',
    'Recovery Readiness': 'Disaster Recovery Status',
    'RTO': 'Recovery Time (How Fast)',
    'RPO': 'Recovery Point (Data Loss Window)',
    'Last Successful Backup': 'Last Data Backup',

    // Identity & Access
    'MFA Coverage': 'Two-Factor Authentication Setup',
    'Global Admins': 'Super Admin Accounts',
    'Privileged Users': 'Admin User Accounts',
    'Risky Users': 'Users Needing Attention',
    'Conditional Access': 'Login Security Rules',
    'PIM': 'Temporary Admin Access',

    // Threats
    'Active Alerts': 'Security Warnings',
    'Threats Blocked': 'Attacks Prevented',
    'Device Compliance': 'Device Security Status',
    'Phishing Blocked': 'Fake Email Attacks Stopped',
    'Malware Blocked': 'Virus Attacks Stopped',

    // IT Accountability
    'Patch SLA Compliance': 'Update Deadline Compliance',
    'MTTR': 'Average Fix Time',
    'Finding Age': 'How Long Issues Stay Open',
    'CVE': 'Known Security Vulnerability',
    'CVSS': 'Vulnerability Severity Rating',

    // Compliance
    'SOC 2': 'Service Security Standard',
    'ISO 27001': 'International Security Standard',
    'CIS': 'Security Best Practices',
    'HIPAA': 'Healthcare Data Rules',
    'PCI-DSS': 'Payment Card Security Rules',

    // Technical Terms
    'Vulnerability': 'Security Weakness',
    'Remediation': 'Fix Action',
    'Audit Trail': 'Activity Log',
    'Non-Compliant': 'Not Meeting Policy',
    'Tenant': 'Organization',
    'Guest Users': 'External Users',
    'Third-Party Apps': 'External Applications',
}

/**
 * Get the simple label for a technical term
 * Returns the original label if no simple version exists
 */
export function getSimpleLabel(technicalLabel: string): string {
    return simpleLabels[technicalLabel] || technicalLabel
}

/**
 * Simple descriptions for metrics
 */
export const simpleDescriptions: Record<string, string> = {
    'Security Score': 'A percentage showing how well protected your organization is. Higher is better.',
    'Compliance Score': 'How well your organization follows security policies and regulations.',
    'MFA Coverage': 'Percentage of users who need to verify their identity with two methods when logging in.',
    'Backup Health': 'Status of your data backups. If something goes wrong, backups help you recover.',
    'Device Compliance': 'Percentage of computers and phones that meet your security requirements.',
    'MTTR': 'The average time it takes to fix a security issue after it is found.',
    'Global Admins': 'Users with full control over your Microsoft 365 environment. Keep this number low.',
}

export function getSimpleDescription(metricName: string): string | undefined {
    return simpleDescriptions[metricName]
}
