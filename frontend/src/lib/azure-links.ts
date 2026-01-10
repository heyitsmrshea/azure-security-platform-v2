export const AZURE_PORTAL_URL = 'https://portal.azure.com'

export const AzureLinks = {
    // Identity & Access (Entra ID)
    users: `${AZURE_PORTAL_URL}/#view/Microsoft_AAD_UsersAndTenants/UserManagementMenuBlade/~/AllUsers`,
    riskyUsers: `${AZURE_PORTAL_URL}/#view/Microsoft_AAD_IAM/RiskyUsersBlade`,
    mfaParams: `${AZURE_PORTAL_URL}/#view/Microsoft_AAD_IAM/AuthenticationMethodsMenuBlade/~/AdminAuthMethods`,
    conditionalAccess: `${AZURE_PORTAL_URL}/#view/Microsoft_AAD_IAM/ConditionalAccessBlade/~/Policies`,

    // Devices (Intune)
    devices: `${AZURE_PORTAL_URL}/#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/allDevices`,
    compliancePolicies: `${AZURE_PORTAL_URL}/#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/compliancePolicies`,

    // Security (Defender)
    securityCenter: 'https://security.microsoft.com',
    incidents: 'https://security.microsoft.com/incidents',
    alerts: 'https://security.microsoft.com/alerts',
    vulnerabilities: 'https://security.microsoft.com/tvm_dashboard',
    secureScore: 'https://security.microsoft.com/securescore',

    // Infrastructure
    backup: `${AZURE_PORTAL_URL}/#blade/Microsoft_Azure_RecoveryServices/VaultsMenuBlade/backupItems`,
    monitor: `${AZURE_PORTAL_URL}/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/overview`,
}

export function getTenantLink(path: string, tenantId?: string) {
    // In a real multi-tenant app, we might append ?tenantId={tenantId} 
    // but standard Azure Portal links often handle context switching via the UI.
    // For specific deep links, we return the direct URL.
    return path
}
