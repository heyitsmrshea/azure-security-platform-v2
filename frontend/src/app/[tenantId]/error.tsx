'use client'

import { useEffect } from 'react'
import { ErrorDisplay } from '@/components/shared/ErrorDisplay'

export default function TenantError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error('Tenant Dashboard Error:', error)
    }, [error])

    return (
        <div className="flex h-full items-center justify-center p-6">
            <ErrorDisplay
                title="Dashboard Error"
                message={error.message || "Failed to load dashboard content."}
                onRetry={reset}
                className="max-w-lg w-full shadow-lg"
            />
        </div>
    )
}
