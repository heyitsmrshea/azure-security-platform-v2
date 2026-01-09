'use client'

import { useMsal, useIsAuthenticated } from '@azure/msal-react'
import { InteractionStatus } from '@azure/msal-browser'
import { loginRequest, apiRequest, isMsalConfigured } from '@/lib/msal-config'
import { apiClient } from '@/lib/api-client'
import { useCallback } from 'react'

export function useAuth() {
  const msalConfigured = isMsalConfigured()
  
  // Only call MSAL hooks if configured
  // If not configured, we're in demo mode
  if (!msalConfigured) {
    return {
      isAuthenticated: true, // Demo mode - always authenticated
      isLoading: false,
      user: {
        name: 'Demo User',
        email: 'demo@example.com',
      },
      login: async () => {},
      logout: async () => {},
      getToken: async () => null,
    }
  }

  // This will only be called if MSAL is configured
  return useMsalAuth()
}

function useMsalAuth() {
  const { instance, accounts, inProgress } = useMsal()
  const isAuthenticated = useIsAuthenticated()

  const user = accounts[0] ? {
    name: accounts[0].name || '',
    email: accounts[0].username || '',
    tenantId: accounts[0].tenantId,
  } : null

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

  const getToken = useCallback(async () => {
    try {
      const account = instance.getActiveAccount()
      if (!account) {
        throw new Error('No active account')
      }

      const response = await instance.acquireTokenSilent({
        ...apiRequest,
        account,
      })

      apiClient.setToken(response.accessToken)
      return response.accessToken
    } catch (error) {
      console.error('Token acquisition error:', error)
      // Fall back to interactive
      try {
        const response = await instance.acquireTokenRedirect(apiRequest)
        return null // Redirect will happen
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
