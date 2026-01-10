'use client'

import { useState, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'
import {
    Shield,
    CheckCircle2,
    XCircle,
    AlertCircle,
    MinusCircle,
    ChevronRight,
    FileArchive
} from 'lucide-react'
import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { ControlMapping } from '@/components/compliance/ControlMapping'
import { EvidenceExport } from '@/components/compliance/EvidenceExport'

// Type definitions for compliance data
interface ComplianceFramework {
    id: string
    name: string
    lookup: string
    description: string
    version?: string
    controls_total: number
    controls_passed: number
    compliance_percent: number
    // Status breakdown counts
    passing: number
    failing: number
    partial: number
    not_applicable: number
    unknown: number // Controls that couldn't be assessed
}

interface ComplianceControl {
    id: string // Used as key and display
    control_id: string
    name: string
    title?: string // Displayed as control name
    description: string
    status_reason?: string // Explanation of why this status
    category: string
    frameworks: string[]
    status: 'pass' | 'fail' | 'partial' | 'unknown'
    evidence_available: boolean
    data_source?: string // What API/data was used
}



export function ComplianceClient({ tenantId }: { tenantId: string }) {
    const [selectedFramework, setSelectedFramework] = useState<string | null>(null)
    const [activeView, setActiveView] = useState<'frameworks' | 'controls' | 'mapping'>('frameworks')
    const [isEvidenceExportOpen, setIsEvidenceExportOpen] = useState(false)

    // Data State
    const [frameworks, setFrameworks] = useState<ComplianceFramework[]>([])
    const [controls, setControls] = useState<ComplianceControl[]>([])
    const [isLoading, setIsLoading] = useState(true)

    const fetchData = useCallback(async () => {
        setIsLoading(true)
        try {
            const { apiClient } = await import('@/lib/api-client')

            // Fetch live compliance data from backend
            const [fwData, ctrlData] = await Promise.all([
                apiClient.getComplianceFrameworks(tenantId) as Promise<{ frameworks: ComplianceFramework[] }>,
                apiClient.getComplianceControls(tenantId) as Promise<{ controls: ComplianceControl[] }>
            ])

            // Extract frameworks list from response
            // Backend returns { frameworks: [...] }
            setFrameworks(fwData.frameworks || [])

            // Extract controls list from response
            // Backend returns { controls: [...], by_category: {...}, ... }
            setControls(ctrlData.controls || [])
        } catch (err) {
            console.error('Failed to fetch compliance data', err)
        } finally {
            setIsLoading(false)
        }
    }, [tenantId])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    const currentFramework = selectedFramework ? frameworks.find(f => f.id === selectedFramework) : null

    const filteredControls = currentFramework
        ? controls.filter(c => c.frameworks.some((f: string) => f === currentFramework.lookup))
        : controls

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pass': return <CheckCircle2 className="w-5 h-5 text-status-success" />
            case 'fail': return <XCircle className="w-5 h-5 text-status-error" />
            case 'partial': return <AlertCircle className="w-5 h-5 text-status-warning" />
            default: return <MinusCircle className="w-5 h-5 text-foreground-muted" />
        }
    }

    const getComplianceColor = (percent: number) => {
        if (percent >= 90) return 'text-status-success'
        if (percent >= 70) return 'text-status-warning'
        return 'text-status-error'
    }

    if (isLoading) {
        return (
            <div className="min-h-screen bg-background-primary flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
                    <p className="text-foreground-muted">Loading compliance data...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background-primary">
            <DashboardHeader
                tenantName={tenantId === 'demo' ? 'Demo Organization' : 'Polaris Consulting LLC'}
                tenantId={tenantId}
                title="Compliance Dashboard"
                minutesAgo={5}
                onRefresh={fetchData}
                isRefreshing={isLoading}
            />

            <main className="p-6 space-y-6">
                {/* View Toggle with Export Button */}
                <div className="flex items-center justify-between border-b border-divider pb-4">
                    <div className="flex items-center gap-2">
                        {(['frameworks', 'controls', 'mapping'] as const).map((view) => (
                            <button
                                key={view}
                                onClick={() => setActiveView(view)}
                                className={cn(
                                    'px-4 py-2 text-sm font-medium rounded-lg transition-colors capitalize',
                                    activeView === view
                                        ? 'bg-accent text-foreground-primary'
                                        : 'text-foreground-secondary hover:text-foreground-primary hover:bg-background-tertiary'
                                )}
                            >
                                {view}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={() => setIsEvidenceExportOpen(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <FileArchive className="w-4 h-4" />
                        <span>Export Evidence Pack</span>
                    </button>
                </div>

                {/* Frameworks View */}
                {activeView === 'frameworks' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {frameworks.map((fw) => (
                            <button
                                key={fw.id}
                                onClick={() => {
                                    setSelectedFramework(fw.id)
                                    setActiveView('controls')
                                }}
                                className="card text-left hover:border-accent/50 transition-colors group"
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                                        <Shield className="w-5 h-5 text-accent" />
                                    </div>
                                    <div className="text-right">
                                        <span className={cn('text-2xl font-bold', getComplianceColor(fw.compliance_percent))}>
                                            {fw.compliance_percent.toFixed(0)}%
                                        </span>
                                        {fw.unknown > 0 && (
                                            <p className="text-xs text-foreground-muted">
                                                {fw.controls_total - fw.unknown} of {fw.controls_total} assessed
                                            </p>
                                        )}
                                    </div>
                                </div>
                                <h3 className="text-sm font-medium text-foreground-primary group-hover:text-accent transition-colors">
                                    {fw.name}
                                </h3>
                                <p className="text-xs text-foreground-muted mt-1 line-clamp-2">{fw.description}</p>
                                <p className="text-xs text-foreground-muted mt-1">Version {fw.version}</p>
                                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-divider">
                                    <div className="flex items-center gap-1" title="Passing">
                                        <CheckCircle2 className="w-3 h-3 text-status-success" />
                                        <span className="text-xs text-foreground-secondary">{fw.passing}</span>
                                    </div>
                                    <div className="flex items-center gap-1" title="Failing">
                                        <XCircle className="w-3 h-3 text-status-error" />
                                        <span className="text-xs text-foreground-secondary">{fw.failing}</span>
                                    </div>
                                    <div className="flex items-center gap-1" title="Partial">
                                        <AlertCircle className="w-3 h-3 text-status-warning" />
                                        <span className="text-xs text-foreground-secondary">{fw.partial}</span>
                                    </div>
                                    {fw.unknown > 0 && (
                                        <div className="flex items-center gap-1" title="Not Assessed">
                                            <MinusCircle className="w-3 h-3 text-foreground-muted" />
                                            <span className="text-xs text-foreground-secondary">{fw.unknown}</span>
                                        </div>
                                    )}
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {/* Controls View */}
                {activeView === 'controls' && (
                    <div className="space-y-4">
                        {selectedFramework && (
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setSelectedFramework(null)}
                                    className="text-sm text-accent hover:underline"
                                >
                                    All Controls
                                </button>
                                <ChevronRight className="w-4 h-4 text-foreground-muted" />
                                <span className="text-sm text-foreground-primary">
                                    {frameworks.find(f => f.id === selectedFramework)?.name}
                                </span>
                            </div>
                        )}

                        <div className="card">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-divider">
                                        <th className="text-left py-3 px-4 text-sm font-medium text-foreground-muted">Control</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-foreground-muted">Category</th>
                                        <th className="text-center py-3 px-4 text-sm font-medium text-foreground-muted">Status</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-foreground-muted">Frameworks</th>
                                        <th className="text-right py-3 px-4 text-sm font-medium text-foreground-muted">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredControls.map((control) => (
                                        <tr key={control.control_id} className="border-b border-divider/50 hover:bg-background-tertiary/50">
                                            <td className="py-3 px-4">
                                                <div>
                                                    <span className="text-xs text-foreground-muted">{control.control_id}</span>
                                                    <p className="text-sm font-medium text-foreground-primary">{control.title}</p>
                                                    {control.status_reason && (
                                                        <p className="text-xs text-foreground-muted mt-1">{control.status_reason}</p>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <div>
                                                    <span className="text-sm text-foreground-secondary">{control.category}</span>
                                                    {control.data_source && (
                                                        <p className="text-xs text-foreground-muted">{control.data_source}</p>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-center">{getStatusIcon(control.status)}</td>
                                            <td className="py-3 px-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {control.frameworks.map((fw: string) => (
                                                        <span key={fw} className="px-2 py-0.5 text-xs bg-background-tertiary rounded text-foreground-secondary">
                                                            {fw}
                                                        </span>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                {control.evidence_available ? (
                                                    <button className="text-accent hover:text-accent-dark text-sm">
                                                        View Evidence
                                                    </button>
                                                ) : (
                                                    <span className="text-xs text-foreground-muted">No evidence</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Mapping View */}
                {activeView === 'mapping' && (
                    <ControlMapping tenantId={tenantId} />
                )}
            </main>

            {/* Evidence Export Modal */}
            <EvidenceExport
                isOpen={isEvidenceExportOpen}
                onClose={() => setIsEvidenceExportOpen(false)}
                tenantId={tenantId}
            />
        </div>
    )
}
