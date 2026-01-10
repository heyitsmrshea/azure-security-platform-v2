'use client'

import { useState, useEffect } from 'react'

import { cn } from '@/lib/utils'
import { CheckCircle2, XCircle, AlertCircle, MinusCircle } from 'lucide-react'

// Mock control-to-framework mapping
const controlMappings = [
    { id: 'AC-001', title: 'Multi-Factor Authentication', status: 'partial', soc2: 'CC6.1', iso27001: 'A.9.4.2', cis: '1.1.1', pci: null, nist: null },
    { id: 'AC-002', title: 'Privileged Access Management', status: 'pass', soc2: 'CC6.2', iso27001: 'A.9.2.3', cis: null, pci: null, nist: null },
    { id: 'AC-003', title: 'Conditional Access Policies', status: 'pass', soc2: 'CC6.1', iso27001: null, cis: '1.1.4', pci: null, nist: null },
    { id: 'DP-001', title: 'Data Encryption at Rest', status: 'pass', soc2: 'CC6.7', iso27001: 'A.10.1.1', cis: null, pci: '3.4', nist: null },
    { id: 'DP-002', title: 'Data Encryption in Transit', status: 'pass', soc2: 'CC6.7', iso27001: 'A.13.1.1', cis: null, pci: '4.1', nist: null },
    { id: 'BC-001', title: 'Backup Frequency', status: 'pass', soc2: 'A1.2', iso27001: 'A.12.3.1', cis: null, pci: null, nist: null },
    { id: 'BC-002', title: 'Backup Testing', status: 'partial', soc2: 'A1.2', iso27001: 'A.12.3.1', cis: null, pci: null, nist: null },
    { id: 'IR-001', title: 'Incident Response Plan', status: 'pass', soc2: 'CC7.3', iso27001: 'A.16.1.1', cis: null, pci: null, nist: 'RS.RP-1' },
    { id: 'VM-001', title: 'Vulnerability Scanning', status: 'pass', soc2: 'CC7.1', iso27001: null, cis: '7.1', pci: '11.2', nist: null },
    { id: 'VM-002', title: 'Patch Management SLA', status: 'fail', soc2: 'CC7.1', iso27001: null, cis: '7.3', pci: null, nist: null },
]

const frameworks = [
    { key: 'soc2', name: 'SOC 2' },
    { key: 'iso27001', name: 'ISO 27001' },
    { key: 'cis', name: 'CIS' },
    { key: 'pci', name: 'PCI-DSS' },
    { key: 'nist', name: 'NIST' },
]

export function ControlMapping({ tenantId }: { tenantId: string }) {
    const [mappings, setMappings] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const { apiClient } = await import('@/lib/api-client')
                const data = await apiClient.getControlMapping(tenantId) as any
                setMappings(data.mappings || [])
            } catch (error) {
                console.error('Failed to fetch control mappings', error)
            } finally {
                setIsLoading(false)
            }
        }
        fetchData()
    }, [tenantId])

    if (isLoading) {
        return <div className="p-8 text-center text-foreground-muted">Loading mappings...</div>
    }
    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pass': return <CheckCircle2 className="w-4 h-4 text-status-success" />
            case 'fail': return <XCircle className="w-4 h-4 text-status-error" />
            case 'partial': return <AlertCircle className="w-4 h-4 text-status-warning" />
            default: return <MinusCircle className="w-4 h-4 text-foreground-muted" />
        }
    }

    const getStatusBg = (status: string) => {
        switch (status) {
            case 'pass': return 'bg-status-success/10'
            case 'fail': return 'bg-status-error/10'
            case 'partial': return 'bg-status-warning/10'
            default: return ''
        }
    }

    return (
        <div className="card overflow-hidden">
            <div className="flex items-center justify-between mb-4">
                <h2 className="section-title">Control-to-Framework Mapping</h2>
                <span className="text-sm text-foreground-muted">
                    {mappings.length} controls mapped
                </span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-divider">
                            <th className="sticky left-0 bg-background-secondary text-left py-3 px-4 text-sm font-medium text-foreground-muted min-w-[200px]">
                                Control
                            </th>
                            <th className="text-center py-3 px-2 text-sm font-medium text-foreground-muted w-10">
                                Status
                            </th>
                            {frameworks.map((fw) => (
                                <th key={fw.key} className="text-center py-3 px-3 text-sm font-medium text-foreground-muted min-w-[80px]">
                                    {fw.name}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {mappings.map((control, idx) => (
                            <tr
                                key={control.id}
                                className={cn(
                                    'border-b border-divider/50 hover:bg-background-tertiary/50 transition-colors',
                                    getStatusBg(control.status)
                                )}
                            >
                                <td className="sticky left-0 bg-background-secondary py-3 px-4">
                                    <div>
                                        <span className="text-xs text-foreground-muted">{control.id}</span>
                                        <p className="text-sm font-medium text-foreground-primary">{control.title}</p>
                                    </div>
                                </td>
                                <td className="text-center py-3 px-2">
                                    {getStatusIcon(control.status)}
                                </td>
                                {frameworks.map((fw) => {
                                    const refKey = `${fw.key}_ref`
                                    const ref = control[refKey] || control[fw.key] // Handle both API format and potential fallback
                                    return (
                                        <td key={fw.key} className="text-center py-3 px-3">
                                            {ref ? (
                                                <span className="px-2 py-1 text-xs font-mono bg-background-tertiary rounded text-foreground-secondary">
                                                    {ref}
                                                </span>
                                            ) : (
                                                <span className="text-xs text-foreground-muted">—</span>
                                            )}
                                        </td>
                                    )
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Legend */}
            <div className="flex items-center gap-6 mt-4 pt-4 border-t border-divider">
                <span className="text-sm text-foreground-muted">Status:</span>
                <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-status-success" />
                    <span className="text-sm text-foreground-secondary">Pass</span>
                </div>
                <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-status-warning" />
                    <span className="text-sm text-foreground-secondary">Partial</span>
                </div>
                <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-status-error" />
                    <span className="text-sm text-foreground-secondary">Fail</span>
                </div>
            </div>
        </div>
    )
}
