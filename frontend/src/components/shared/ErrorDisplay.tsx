'use client'

import { AlertTriangle, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ErrorDisplayProps {
    title?: string
    message?: string
    onRetry?: () => void
    className?: string
}

export function ErrorDisplay({
    title = 'Something went wrong',
    message = 'An error occurred while loading this content.',
    onRetry,
    className
}: ErrorDisplayProps) {
    return (
        <div className={cn(
            'flex flex-col items-center justify-center p-8 text-center rounded-lg border border-divider bg-background-secondary/50',
            className
        )}>
            <div className="w-12 h-12 rounded-full bg-status-error/10 flex items-center justify-center mb-4">
                <AlertTriangle className="w-6 h-6 text-status-error" />
            </div>
            <h3 className="text-lg font-semibold text-foreground-primary mb-2">
                {title}
            </h3>
            <p className="text-sm text-foreground-secondary max-w-md mb-6">
                {message}
            </p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="btn-secondary flex items-center gap-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    <span>Try Again</span>
                </button>
            )}
        </div>
    )
}
