import { Configuration, LogLevel } from '@azure/msal-browser'

// MSAL configuration for Azure AD authentication
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_AD_CLIENT_ID || '',
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_AD_TENANT_ID || 'common'}`,
    redirectUri: typeof window !== 'undefined' ? window.location.origin : '',
    postLogoutRedirectUri: typeof window !== 'undefined' ? window.location.origin : '',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return
        switch (level) {
          case LogLevel.Error:
            console.error(message)
            break
          case LogLevel.Warning:
            console.warn(message)
            break
          case LogLevel.Info:
            console.info(message)
            break
          case LogLevel.Verbose:
            console.debug(message)
            break
        }
      },
      logLevel: LogLevel.Warning,
    },
  },
}

// Scopes for API access
export const loginRequest = {
  scopes: ['User.Read', 'openid', 'profile', 'email'],
}

// Scopes for backend API
export const apiRequest = {
  scopes: [`api://${process.env.NEXT_PUBLIC_AZURE_AD_CLIENT_ID}/access_as_user`],
}

// Check if MSAL is configured
export const isMsalConfigured = () => {
  return !!process.env.NEXT_PUBLIC_AZURE_AD_CLIENT_ID && 
         !!process.env.NEXT_PUBLIC_AZURE_AD_TENANT_ID
}
