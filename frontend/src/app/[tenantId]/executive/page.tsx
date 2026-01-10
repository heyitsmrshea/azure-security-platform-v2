import { ExecutiveClient } from './ExecutiveClient'

// Generate static params for export
export function generateStaticParams() {
  return [
    { tenantId: 'demo' },
    { tenantId: 'acme-corp' },
    { tenantId: 'globex' },
    { tenantId: 'initech' },
    { tenantId: 'cf47a479-9ed1-452d-896a-0e362307e969' }, // Polaris Consulting
  ]
}

export default function ExecutiveDashboardPage({
  params,
}: {
  params: { tenantId: string }
}) {
  return <ExecutiveClient tenantId={params.tenantId} />
}
