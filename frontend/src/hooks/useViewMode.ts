'use client'

import { useState, useEffect, useCallback } from 'react'
import { getSimpleLabel } from '@/lib/simple-labels'

const STORAGE_KEY = 'security-dashboard-view-mode'

export type ViewMode = 'technical' | 'simplified'

export interface UseViewModeResult {
    viewMode: ViewMode
    isSimplified: boolean
    toggleViewMode: () => void
    setViewMode: (mode: ViewMode) => void
    getLabel: (technicalLabel: string) => string
}

/**
 * Hook to manage technical/simplified view mode
 * Persists preference to localStorage
 */
export function useViewMode(): UseViewModeResult {
    const [viewMode, setViewModeState] = useState<ViewMode>('technical')
    const [isHydrated, setIsHydrated] = useState(false)

    // Load saved preference on mount
    useEffect(() => {
        const saved = localStorage.getItem(STORAGE_KEY) as ViewMode | null
        if (saved && (saved === 'technical' || saved === 'simplified')) {
            setViewModeState(saved)
        }
        setIsHydrated(true)
    }, [])

    // Save preference when it changes
    const setViewMode = useCallback((mode: ViewMode) => {
        setViewModeState(mode)
        localStorage.setItem(STORAGE_KEY, mode)
    }, [])

    const toggleViewMode = useCallback(() => {
        setViewMode(viewMode === 'technical' ? 'simplified' : 'technical')
    }, [viewMode, setViewMode])

    // Get the appropriate label based on view mode
    const getLabel = useCallback((technicalLabel: string) => {
        if (viewMode === 'simplified') {
            return getSimpleLabel(technicalLabel)
        }
        return technicalLabel
    }, [viewMode])

    return {
        viewMode,
        isSimplified: viewMode === 'simplified',
        toggleViewMode,
        setViewMode,
        getLabel,
    }
}
