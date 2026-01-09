import { ComplianceClient } from './ComplianceClient'

// Generate static params for export
export function generateStaticParams() {
    return [
        { tenantId: 'demo' },
        { tenantId: 'acme-corp' },
        { tenantId: 'globex' },
        { tenantId: 'initech' },
    ]
}

export default function CompliancePage({
    params,
}: {
    params: { tenantId: string }
}) {
    return <ComplianceClient tenantId={params.tenantId} />
}
