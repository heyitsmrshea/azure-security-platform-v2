'use client'

import { ReactNode, useEffect, useState } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { MsalProvider } from '@azure/msal-react'
import { PublicClientApplication, EventType, EventMessage, AuthenticationResult } from '@azure/msal-browser'
import { queryClient } from '@/lib/query-client'
import { msalConfig, isMsalConfigured } from '@/lib/msal-config'
import { apiClient } from '@/lib/api-client'

interface ProvidersProps {
  children: ReactNode
}

// Initialize MSAL instance (only if configured)
let msalInstance: PublicClientApplication | null = null
if (typeof window !== 'undefined' && isMsalConfigured()) {
  msalInstance = new PublicClientApplication(msalConfig)
}

export function Providers({ children }: ProvidersProps) {
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    const initializeMsal = async () => {
      if (msalInstance) {
        try {
          await msalInstance.initialize()
          
          // Handle redirect response
          const response = await msalInstance.handleRedirectPromise()
          if (response) {
            apiClient.setToken(response.accessToken)
          }

          // Set up event callback for token acquisition
          msalInstance.addEventCallback((event: EventMessage) => {
            if (event.eventType === EventType.LOGIN_SUCCESS || 
                event.eventType === EventType.ACQUIRE_TOKEN_SUCCESS) {
              const payload = event.payload as AuthenticationResult
              if (payload.accessToken) {
                apiClient.setToken(payload.accessToken)
              }
            }
            if (event.eventType === EventType.LOGOUT_SUCCESS) {
              apiClient.setToken(null)
            }
          })

          // Check for existing account
          const accounts = msalInstance.getAllAccounts()
          if (accounts.length > 0) {
            msalInstance.setActiveAccount(accounts[0])
          }
        } catch (error) {
          console.error('MSAL initialization error:', error)
        }
      }
      setIsInitialized(true)
    }

    initializeMsal()
  }, [])

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background-primary">
        <div className="animate-pulse text-foreground-secondary">
          Initializing...
        </div>
      </div>
    )
  }

  // If MSAL is configured, wrap with MsalProvider
  if (msalInstance) {
    return (
      <MsalProvider instance={msalInstance}>
        <QueryClientProvider client={queryClient}>
          {children}
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </MsalProvider>
    )
  }

  // If MSAL is not configured, just use QueryClientProvider
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
