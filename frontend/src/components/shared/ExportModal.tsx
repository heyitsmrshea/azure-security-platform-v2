'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { X, Download, FileText, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface ExportModalProps {
    isOpen: boolean
    onClose: () => void
    tenantId: string
    dashboardType: 'executive' | 'it-staff'
}

type ReportType = 'executive' | 'compliance' | 'vulnerability' | 'audit'
type ReportFormat = 'pdf' | 'csv'

const reportTypes: { id: ReportType; name: string; description: string }[] = [
    { id: 'executive', name: 'Executive Summary', description: 'High-level security posture for board/executives' },
    { id: 'compliance', name: 'Compliance Report', description: 'Detailed compliance status against frameworks' },
    { id: 'vulnerability', name: 'Vulnerability Report', description: 'Current vulnerabilities and remediation status' },
    { id: 'audit', name: 'Audit Trail', description: 'Administrative actions and changes' },
]

export function ExportModal({ isOpen, onClose, tenantId, dashboardType: _dashboardType }: ExportModalProps) {
    void _dashboardType // Available for filtering report types by dashboard context
    const [selectedType, setSelectedType] = useState<ReportType>('executive')
    const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('pdf')
    const [dateRange, setDateRange] = useState(30)
    const [isGenerating, setIsGenerating] = useState(false)
    const [error, setError] = useState<string | null>(null)

    if (!isOpen) return null

    const handleExport = async () => {
        setIsGenerating(true)
        setError(null)

        try {
            const response = await apiClient.generateReport(tenantId, {
                report_type: selectedType,
                format: selectedFormat,
                date_range_days: dateRange,
            }) as { report_id?: string; success?: boolean; format?: string }

            // Trigger download with format parameter
            if (response.report_id) {
                const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
                const downloadUrl = `${apiBase}/${tenantId}/reports/download/${response.report_id}?format=${selectedFormat}`
                
                // Open download in new tab
                window.open(downloadUrl, '_blank')
                onClose()
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate report')
        } finally {
            setIsGenerating(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-lg mx-4 bg-background-secondary border border-divider rounded-xl shadow-2xl">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-divider">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                            <Download className="w-5 h-5 text-accent" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-foreground-primary">Export Report</h2>
                            <p className="text-sm text-foreground-muted">Generate and download a report</p>
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
                <div className="px-6 py-4 space-y-6">
                    {/* Report Type Selection */}
                    <div>
                        <label className="block text-sm font-medium text-foreground-secondary mb-3">
                            Report Type
                        </label>
                        <div className="space-y-2">
                            {reportTypes.map((type) => (
                                <button
                                    key={type.id}
                                    onClick={() => setSelectedType(type.id)}
                                    className={cn(
                                        'w-full flex items-start gap-3 p-3 rounded-lg border transition-all text-left',
                                        selectedType === type.id
                                            ? 'border-accent bg-accent/5'
                                            : 'border-divider hover:border-foreground-muted/30'
                                    )}
                                >
                                    <FileText className={cn(
                                        'w-5 h-5 mt-0.5',
                                        selectedType === type.id ? 'text-accent' : 'text-foreground-muted'
                                    )} />
                                    <div>
                                        <p className={cn(
                                            'text-sm font-medium',
                                            selectedType === type.id ? 'text-foreground-primary' : 'text-foreground-secondary'
                                        )}>
                                            {type.name}
                                        </p>
                                        <p className="text-xs text-foreground-muted mt-0.5">{type.description}</p>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Format Selection */}
                    <div>
                        <label className="block text-sm font-medium text-foreground-secondary mb-3">
                            Format
                        </label>
                        <div className="flex gap-3">
                            {(['pdf', 'csv'] as const).map((format) => (
                                <button
                                    key={format}
                                    onClick={() => setSelectedFormat(format)}
                                    className={cn(
                                        'flex-1 py-2 px-4 rounded-lg border text-sm font-medium uppercase transition-all',
                                        selectedFormat === format
                                            ? 'border-accent bg-accent/10 text-accent'
                                            : 'border-divider text-foreground-secondary hover:border-foreground-muted/30'
                                    )}
                                >
                                    {format}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Date Range */}
                    <div>
                        <label className="block text-sm font-medium text-foreground-secondary mb-3">
                            Date Range
                        </label>
                        <select
                            value={dateRange}
                            onChange={(e) => setDateRange(Number(e.target.value))}
                            className="w-full px-4 py-2 rounded-lg border border-divider bg-background-tertiary text-foreground-primary text-sm focus:outline-none focus:border-accent"
                        >
                            <option value={7}>Last 7 days</option>
                            <option value={30}>Last 30 days</option>
                            <option value={90}>Last 90 days</option>
                            <option value={180}>Last 6 months</option>
                        </select>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="p-3 rounded-lg bg-status-error/10 border border-status-error/30">
                            <p className="text-sm text-status-error">{error}</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-divider">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-foreground-secondary hover:text-foreground-primary transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleExport}
                        disabled={isGenerating}
                        className="btn-primary flex items-center gap-2"
                    >
                        {isGenerating ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Generating...</span>
                            </>
                        ) : (
                            <>
                                <Download className="w-4 h-4" />
                                <span>Export</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
