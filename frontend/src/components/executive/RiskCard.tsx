'use client'

import { cn, getSeverityColor, getSeverityBgColor } from '@/lib/utils'
import { AlertTriangle, ChevronRight } from 'lucide-react'
import { TopRisk } from '@/types/dashboard'

interface RiskCardProps {
  risks: TopRisk[]
  className?: string
}

export function RiskCard({ risks, className }: RiskCardProps) {
  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-severity-high" />
          Top Risks
        </h3>
        <button className="text-sm text-accent hover:text-accent-hover transition-colors flex items-center gap-1">
          View all
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        {risks.map((risk, index) => (
          <RiskItem key={index} risk={risk} />
        ))}
      </div>
    </div>
  )
}

interface RiskItemProps {
  risk: TopRisk
}

function RiskItem({ risk }: RiskItemProps) {
  return (
    <div className="p-3 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors">
      <div className="flex items-start gap-3">
        {/* Severity Indicator */}
        <div className={cn(
          'w-2 h-2 mt-2 rounded-full flex-shrink-0',
          risk.severity === 'critical' && 'bg-severity-critical',
          risk.severity === 'high' && 'bg-severity-high',
          risk.severity === 'medium' && 'bg-severity-medium',
          risk.severity === 'low' && 'bg-severity-low',
        )} />

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-medium text-foreground-primary text-sm">
              {risk.title}
            </h4>
            <span className={cn(
              'text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0',
              getSeverityBgColor(risk.severity),
              getSeverityColor(risk.severity),
            )}>
              {risk.affected_resources} affected
            </span>
          </div>
          
          <p className="text-sm text-foreground-muted mt-1 line-clamp-2">
            {risk.description}
          </p>

          <p className="text-xs text-accent mt-2">
            {risk.recommendation}
          </p>
        </div>
      </div>
    </div>
  )
}
