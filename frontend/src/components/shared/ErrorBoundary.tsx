'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import Link from 'next/link'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onReset?: () => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

/**
 * Error Boundary component for graceful error handling.
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs errors, and displays a fallback UI.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({ errorInfo })
    
    // In production, you could send this to an error reporting service
    // e.g., Sentry, Application Insights, etc.
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
    this.props.onReset?.()
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center">
            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-status-error/10 flex items-center justify-center">
              <AlertTriangle className="w-8 h-8 text-status-error" />
            </div>
            
            <h2 className="text-xl font-semibold text-foreground-primary mb-2">
              Something went wrong
            </h2>
            
            <p className="text-foreground-muted mb-6">
              An error occurred while loading this component. 
              This may be due to a network issue or missing data.
            </p>

            {/* Error details in development */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 rounded-lg bg-background-tertiary text-left overflow-auto max-h-32">
                <p className="text-sm text-status-error font-mono">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleReset}
                className="btn-primary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
              
              <Link
                href="/"
                className="btn-secondary flex items-center gap-2"
              >
                <Home className="w-4 h-4" />
                Go Home
              </Link>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook-based error boundary wrapper for functional components.
 * Use this to wrap sections that might fail without crashing the whole page.
 */
interface ErrorFallbackProps {
  error: Error
  resetError: () => void
}

export function ErrorFallback({ error, resetError }: ErrorFallbackProps) {
  return (
    <div className="p-4 rounded-lg border border-status-error/30 bg-status-error/5">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-status-error flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-medium text-foreground-primary mb-1">
            Failed to load data
          </p>
          <p className="text-sm text-foreground-muted mb-3">
            {error.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={resetError}
            className="text-sm font-medium text-accent hover:underline flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Inline error display for metric cards that fail to load.
 */
interface MetricErrorProps {
  message?: string
  onRetry?: () => void
}

export function MetricError({ message = 'Unable to load', onRetry }: MetricErrorProps) {
  return (
    <div className="card border-l-4 border-l-status-error/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-foreground-muted">
          <AlertTriangle className="w-4 h-4 text-status-error/70" />
          <span className="text-sm">{message}</span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs text-accent hover:underline flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Permission denied message for metrics requiring additional Graph API permissions.
 */
interface PermissionRequiredProps {
  feature: string
  permission?: string
  documentationUrl?: string
}

export function PermissionRequired({ 
  feature, 
  permission,
  documentationUrl = 'https://docs.microsoft.com/graph/permissions-reference'
}: PermissionRequiredProps) {
  return (
    <div className="card border-l-4 border-l-status-warning/50">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-status-warning/10 flex items-center justify-center flex-shrink-0">
          <AlertTriangle className="w-4 h-4 text-status-warning" />
        </div>
        <div>
          <p className="text-sm font-medium text-foreground-primary mb-1">
            {feature} requires additional permissions
          </p>
          {permission && (
            <p className="text-xs text-foreground-muted mb-2">
              Required: <code className="bg-background-tertiary px-1 py-0.5 rounded">{permission}</code>
            </p>
          )}
          <a
            href={documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-accent hover:underline"
          >
            Learn more about permissions →
          </a>
        </div>
      </div>
    </div>
  )
}

export default ErrorBoundary
