'use client'

import { cn } from '@/lib/utils'
import { Download, X, Trash2, CheckSquare, Archive } from 'lucide-react'

interface BulkActionBarProps {
    selectedCount: number
    totalCount: number
    onSelectAll: () => void
    onClearSelection: () => void
    onExport: () => void
    onResolve?: () => void
    onDismiss?: () => void
    className?: string
}

export function BulkActionBar({
    selectedCount,
    totalCount,
    onSelectAll,
    onClearSelection,
    onExport,
    onResolve,
    onDismiss,
    className,
}: BulkActionBarProps) {
    if (selectedCount === 0) return null

    return (
        <div
            className={cn(
                'fixed bottom-6 left-1/2 -translate-x-1/2 z-40',
                'flex items-center gap-4 px-6 py-3',
                'bg-background-secondary border border-divider rounded-xl shadow-2xl',
                'animate-in slide-in-from-bottom-4 duration-300',
                className
            )}
        >
            {/* Selection Info */}
            <div className="flex items-center gap-3 pr-4 border-r border-divider">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                    <CheckSquare className="w-4 h-4 text-accent" />
                </div>
                <div>
                    <p className="text-sm font-medium text-foreground-primary">
                        {selectedCount} selected
                    </p>
                    <p className="text-xs text-foreground-muted">
                        of {totalCount} items
                    </p>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
                {/* Select All */}
                {selectedCount < totalCount && (
                    <button
                        onClick={onSelectAll}
                        className="px-3 py-2 text-sm font-medium text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary rounded-lg transition-colors"
                    >
                        Select All
                    </button>
                )}

                {/* Export */}
                <button
                    onClick={onExport}
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary rounded-lg transition-colors"
                >
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                </button>

                {/* Resolve (for alerts/vulnerabilities) */}
                {onResolve && (
                    <button
                        onClick={onResolve}
                        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-status-success hover:bg-status-success/10 rounded-lg transition-colors"
                    >
                        <Archive className="w-4 h-4" />
                        <span>Resolve</span>
                    </button>
                )}

                {/* Dismiss */}
                {onDismiss && (
                    <button
                        onClick={onDismiss}
                        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-status-warning hover:bg-status-warning/10 rounded-lg transition-colors"
                    >
                        <Trash2 className="w-4 h-4" />
                        <span>Dismiss</span>
                    </button>
                )}
            </div>

            {/* Close Button */}
            <button
                onClick={onClearSelection}
                className="p-2 text-foreground-muted hover:text-foreground-primary hover:bg-background-tertiary rounded-lg transition-colors ml-2"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    )
}
