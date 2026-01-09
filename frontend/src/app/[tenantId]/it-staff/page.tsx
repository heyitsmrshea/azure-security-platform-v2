import { ITStaffClient } from './ITStaffClient'

// Generate static params for export
export function generateStaticParams() {
  return [
    { tenantId: 'demo' },
    { tenantId: 'acme-corp' },
    { tenantId: 'globex' },
    { tenantId: 'initech' },
  ]
}

export default function ITStaffDashboardPage({
  params,
}: {
  params: { tenantId: string }
}) {
  return <ITStaffClient tenantId={params.tenantId} />
}
