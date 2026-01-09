'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { X, Download, FileArchive, Check, Loader2, Calendar } from 'lucide-react'

interface EvidenceExportProps {
    isOpen: boolean
    onClose: () => void
    tenantId: string
}

const evidenceTypes = [
    { id: 'mfa_config', name: 'MFA Configuration', description: 'Azure AD MFA policies and enrollment status' },
    { id: 'mfa_report', name: 'MFA Enrollment Report', description: 'List of all users and their MFA status' },
    { id: 'access_logs', name: 'Access Logs', description: 'Sign-in logs and access audit trail' },
    { id: 'ca_policies', name: 'Conditional Access Policies', description: 'All CA policies with configurations' },
    { id: 'admin_roles', name: 'Admin Role Assignments', description: 'Privileged role assignments and PIM status' },
    { id: 'device_compliance', name: 'Device Compliance Report', description: 'Intune device compliance status' },
    { id: 'backup_status', name: 'Backup Status', description: 'Azure Backup vault and job status' },
    { id: 'security_score', name: 'Security Score Snapshot', description: 'Current security score with recommendations' },
]

export function EvidenceExport({ isOpen, onClose, tenantId }: EvidenceExportProps) {
    const [selectedTypes, setSelectedTypes] = useState<string[]>([])
    const [dateRange, setDateRange] = useState(90)
    const [isGenerating, setIsGenerating] = useState(false)
    const [progress, setProgress] = useState(0)

    if (!isOpen) return null

    const toggleType = (typeId: string) => {
        setSelectedTypes(prev =>
            prev.includes(typeId)
                ? prev.filter(t => t !== typeId)
                : [...prev, typeId]
        )
    }

    const selectAll = () => {
        setSelectedTypes(evidenceTypes.map(t => t.id))
    }

    const clearAll = () => {
        setSelectedTypes([])
    }

    const handleExport = async () => {
        if (selectedTypes.length === 0) return

        setIsGenerating(true)
        setProgress(0)

        // Simulate progress
        for (let i = 0; i <= 100; i += 10) {
            await new Promise(resolve => setTimeout(resolve, 200))
            setProgress(i)
        }

        // Trigger download (in production this would be a real file)
        const link = document.createElement('a')
        link.href = `/api/${tenantId}/reports/evidence-pack`
        link.download = `evidence-pack-${tenantId}-${new Date().toISOString().split('T')[0]}.zip`
        // link.click()

        setIsGenerating(false)
        onClose()
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl mx-4 bg-background-secondary border border-divider rounded-xl shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-divider shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                            <FileArchive className="w-5 h-5 text-accent" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-foreground-primary">Export Evidence Pack</h2>
                            <p className="text-sm text-foreground-muted">Select evidence types for audit</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-background-tertiary transition-colors"
                    >
                        <X className="w-5 h-5 text-foreground-muted" />
                    </button>
                </div>

                {/* Content */}
                <div className="px-6 py-4 space-y-6 overflow-y-auto flex-1">
                    {/* Date Range */}
                    <div>
                        <label className="flex items-center gap-2 text-sm font-medium text-foreground-secondary mb-3">
                            <Calendar className="w-4 h-4" />
                            Date Range
                        </label>
                        <div className="flex gap-3">
                            {[30, 90, 180, 365].map((days) => (
                                <button
                                    key={days}
                                    onClick={() => setDateRange(days)}
                                    className={cn(
                                        'flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-all',
                                        dateRange === days
                                            ? 'border-accent bg-accent/10 text-accent'
                                            : 'border-divider text-foreground-secondary hover:border-foreground-muted/30'
                                    )}
                                >
                                    {days < 365 ? `${days} days` : '1 year'}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Evidence Types */}
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <label className="text-sm font-medium text-foreground-secondary">
                                Evidence Types
                            </label>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={selectAll}
                                    className="text-xs text-accent hover:underline"
                                >
                                    Select All
                                </button>
                                <span className="text-foreground-muted">|</span>
                                <button
                                    onClick={clearAll}
                                    className="text-xs text-foreground-muted hover:text-foreground-secondary"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {evidenceTypes.map((type) => (
                                <button
                                    key={type.id}
                                    onClick={() => toggleType(type.id)}
                                    className={cn(
                                        'flex items-start gap-3 p-3 rounded-lg border text-left transition-all',
                                        selectedTypes.includes(type.id)
                                            ? 'border-accent bg-accent/5'
                                            : 'border-divider hover:border-foreground-muted/30'
                                    )}
                                >
                                    <div className={cn(
                                        'w-5 h-5 rounded border flex items-center justify-center shrink-0 mt-0.5',
                                        selectedTypes.includes(type.id)
                                            ? 'bg-accent border-accent'
                                            : 'border-foreground-muted'
                                    )}>
                                        {selectedTypes.includes(type.id) && (
                                            <Check className="w-3 h-3 text-white" />
                                        )}
                                    </div>
                                    <div>
                                        <p className={cn(
                                            'text-sm font-medium',
                                            selectedTypes.includes(type.id) ? 'text-foreground-primary' : 'text-foreground-secondary'
                                        )}>
                                            {type.name}
                                        </p>
                                        <p className="text-xs text-foreground-muted mt-0.5">{type.description}</p>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Progress */}
                    {isGenerating && (
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-foreground-secondary">Generating evidence pack...</span>
                                <span className="text-foreground-primary font-medium">{progress}%</span>
                            </div>
                            <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-accent rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-6 py-4 border-t border-divider shrink-0">
                    <span className="text-sm text-foreground-muted">
                        {selectedTypes.length} of {evidenceTypes.length} selected
                    </span>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-foreground-secondary hover:text-foreground-primary transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleExport}
                            disabled={isGenerating || selectedTypes.length === 0}
                            className={cn(
                                'btn-primary flex items-center gap-2',
                                (isGenerating || selectedTypes.length === 0) && 'opacity-50 cursor-not-allowed'
                            )}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Generating...</span>
                                </>
                            ) : (
                                <>
                                    <Download className="w-4 h-4" />
                                    <span>Export ZIP</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
