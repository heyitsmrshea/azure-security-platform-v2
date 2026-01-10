'use client'

import { useEffect } from 'react'
import { ErrorDisplay } from '@/components/shared/ErrorDisplay'

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error('Global Application Error:', error)
    }, [error])

    return (
        <div className="flex min-h-screen items-center justify-center bg-background-primary p-6">
            <ErrorDisplay
                title="Application Error"
                message={error.message || "A critical error specific to the application occurred."}
                onRetry={reset}
                className="max-w-xl w-full bg-background-secondary shadow-xl"
            />
        </div>
    )
}
