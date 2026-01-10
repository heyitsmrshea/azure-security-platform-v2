'use client'

/* eslint-disable react-hooks/rules-of-hooks */
// Note: The conditional hook pattern below is safe because isMsalConfigured() 
// is evaluated at module load time and never changes during runtime.
// This is a known pattern for optional provider hooks.

import { useMsal, useIsAuthenticated } from '@azure/msal-react'
import { InteractionStatus } from '@azure/msal-browser'
import { loginRequest, apiRequest, isMsalConfigured } from '@/lib/msal-config'
import { apiClient } from '@/lib/api-client'
import { useCallback, useMemo } from 'react'

// Check at module load time - this never changes during runtime
const msalConfigured = isMsalConfigured()

// Demo mode auth result - used when MSAL is not configured
const demoAuthResult = {
  isAuthenticated: true,
  isLoading: false,
  user: {
    name: 'Demo User',
    email: 'demo@example.com',
    tenantId: undefined as string | undefined,
  },
  login: async () => {},
  logout: async () => {},
  getToken: async (): Promise<string | null> => null,
}

export function useAuth() {
  // Early return for demo mode - hooks below won't be called
  // This is safe because msalConfigured is constant at module level
  if (!msalConfigured) {
    return demoAuthResult
  }

  // MSAL hooks - only called when MSAL is configured
  const { instance, accounts, inProgress } = useMsal()
  const isAuthenticated = useIsAuthenticated()

  const user = useMemo(() => accounts[0] ? {
    name: accounts[0].name || '',
    email: accounts[0].username || '',
    tenantId: accounts[0].tenantId,
  } : null, [accounts])

  const login = useCallback(async () => {
    try {
      await instance.loginRedirect(loginRequest)
    } catch (error) {
      console.error('Login error:', error)
    }
  }, [instance])

  const logout = useCallback(async () => {
    try {
      await instance.logoutRedirect()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }, [instance])

  const getToken = useCallback(async (): Promise<string | null> => {
    try {
      const account = instance.getActiveAccount()
      if (!account) {
        throw new Error('No active account')
      }

      const tokenResponse = await instance.acquireTokenSilent({
        ...apiRequest,
        account,
      })

      apiClient.setToken(tokenResponse.accessToken)
      return tokenResponse.accessToken
    } catch (error) {
      console.error('Token acquisition error:', error)
      try {
        await instance.acquireTokenRedirect(apiRequest)
        return null
      } catch (interactiveError) {
        console.error('Interactive token error:', interactiveError)
        return null
      }
    }
  }, [instance])

  return {
    isAuthenticated,
    isLoading: inProgress !== InteractionStatus.None,
    user,
    login,
    logout,
    getToken,
  }
}
