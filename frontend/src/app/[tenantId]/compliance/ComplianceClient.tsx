'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import {
    Shield,
    CheckCircle2,
    XCircle,
    AlertCircle,
    MinusCircle,
    Download,
    ChevronDown,
    ChevronRight,
    FileCheck,
    FileArchive
} from 'lucide-react'
import { DashboardHeader } from '@/components/shared/DashboardHeader'
import { ControlMapping } from '@/components/compliance/ControlMapping'
import { EvidenceExport } from '@/components/compliance/EvidenceExport'

// Mock data
const mockFrameworks = [
    { id: 'soc2', name: 'SOC 2 Type II', version: '2017', compliance_percent: 85.0, total: 10, passing: 7, failing: 1, partial: 2 },
    { id: 'iso27001', name: 'ISO/IEC 27001', version: '2022', compliance_percent: 80.0, total: 8, passing: 6, failing: 0, partial: 2 },
    { id: 'cis', name: 'CIS Azure Benchmark', version: '2.0', compliance_percent: 75.0, total: 6, passing: 4, failing: 1, partial: 1 },
    { id: 'pci', name: 'PCI DSS', version: '4.0', compliance_percent: 100.0, total: 3, passing: 3, failing: 0, partial: 0 },
]

const mockControls = [
    { id: 'AC-001', title: 'Multi-Factor Authentication Required', status: 'partial', category: 'Access Control', frameworks: ['SOC 2', 'ISO 27001', 'CIS'] },
    { id: 'AC-002', title: 'Privileged Access Management', status: 'pass', category: 'Access Control', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'AC-003', title: 'Conditional Access Policies', status: 'pass', category: 'Access Control', frameworks: ['SOC 2', 'CIS'] },
    { id: 'DP-001', title: 'Data Encryption at Rest', status: 'pass', category: 'Data Protection', frameworks: ['SOC 2', 'ISO 27001', 'PCI-DSS'] },
    { id: 'DP-002', title: 'Data Encryption in Transit', status: 'pass', category: 'Data Protection', frameworks: ['SOC 2', 'ISO 27001', 'PCI-DSS'] },
    { id: 'BC-001', title: 'Backup Frequency', status: 'pass', category: 'Business Continuity', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'BC-002', title: 'Backup Testing', status: 'partial', category: 'Business Continuity', frameworks: ['SOC 2', 'ISO 27001'] },
    { id: 'IR-001', title: 'Incident Response Plan', status: 'pass', category: 'Incident Response', frameworks: ['SOC 2', 'ISO 27001', 'NIST'] },
    { id: 'VM-001', title: 'Vulnerability Scanning', status: 'pass', category: 'Vulnerability Mgmt', frameworks: ['SOC 2', 'CIS', 'PCI-DSS'] },
    { id: 'VM-002', title: 'Patch Management SLA', status: 'fail', category: 'Vulnerability Mgmt', frameworks: ['SOC 2', 'CIS'] },
]

export function ComplianceClient({ tenantId }: { tenantId: string }) {
    const [selectedFramework, setSelectedFramework] = useState<string | null>(null)
    const [activeView, setActiveView] = useState<'frameworks' | 'controls' | 'mapping'>('frameworks')
    const [isEvidenceExportOpen, setIsEvidenceExportOpen] = useState(false)

    const filteredControls = selectedFramework
        ? mockControls.filter(c => c.frameworks.some(f => f.toLowerCase().includes(selectedFramework.toLowerCase())))
        : mockControls

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

    return (
        <div className="min-h-screen bg-background-primary">
            <DashboardHeader
                tenantName="Demo Organization"
                tenantId={tenantId}
                title="Compliance Dashboard"
                minutesAgo={5}
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
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {mockFrameworks.map((fw) => (
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
                                    <span className={cn('text-2xl font-bold', getComplianceColor(fw.compliance_percent))}>
                                        {fw.compliance_percent.toFixed(0)}%
                                    </span>
                                </div>
                                <h3 className="text-sm font-medium text-foreground-primary group-hover:text-accent transition-colors">
                                    {fw.name}
                                </h3>
                                <p className="text-xs text-foreground-muted mt-1">Version {fw.version}</p>
                                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-divider">
                                    <div className="flex items-center gap-1">
                                        <CheckCircle2 className="w-3 h-3 text-status-success" />
                                        <span className="text-xs text-foreground-secondary">{fw.passing}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <XCircle className="w-3 h-3 text-status-error" />
                                        <span className="text-xs text-foreground-secondary">{fw.failing}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <AlertCircle className="w-3 h-3 text-status-warning" />
                                        <span className="text-xs text-foreground-secondary">{fw.partial}</span>
                                    </div>
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
                                    {mockFrameworks.find(f => f.id === selectedFramework)?.name}
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
                                        <tr key={control.id} className="border-b border-divider/50 hover:bg-background-tertiary/50">
                                            <td className="py-3 px-4">
                                                <div>
                                                    <span className="text-xs text-foreground-muted">{control.id}</span>
                                                    <p className="text-sm font-medium text-foreground-primary">{control.title}</p>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-sm text-foreground-secondary">{control.category}</td>
                                            <td className="py-3 px-4 text-center">{getStatusIcon(control.status)}</td>
                                            <td className="py-3 px-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {control.frameworks.map((fw) => (
                                                        <span key={fw} className="px-2 py-0.5 text-xs bg-background-tertiary rounded text-foreground-secondary">
                                                            {fw}
                                                        </span>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <button className="text-accent hover:text-accent-dark text-sm">
                                                    View Evidence
                                                </button>
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
                    <ControlMapping />
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
