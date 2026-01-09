import { ExecutiveClient } from './ExecutiveClient'

// Generate static params for export
export function generateStaticParams() {
  return [
    { tenantId: 'demo' },
    { tenantId: 'acme-corp' },
    { tenantId: 'globex' },
    { tenantId: 'initech' },
  ]
}

export default function ExecutiveDashboardPage({
  params,
}: {
  params: { tenantId: string }
}) {
  return <ExecutiveClient tenantId={params.tenantId} />
}
