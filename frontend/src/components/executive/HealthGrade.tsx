'use client'

import { cn } from '@/lib/utils'

interface HealthGradeProps {
  score: number
  className?: string
  showLabel?: boolean
}

/**
 * Calculate letter grade from security score
 * A = 90-100
 * B = 80-89
 * C = 70-79
 * D = 60-69
 * F = 0-59
 */
function getGradeFromScore(score: number): { letter: string; color: string; bgColor: string } {
  if (score >= 90) {
    return { letter: 'A', color: 'text-status-success', bgColor: 'bg-status-success/10' }
  } else if (score >= 80) {
    return { letter: 'B', color: 'text-status-success', bgColor: 'bg-status-success/10' }
  } else if (score >= 70) {
    return { letter: 'C', color: 'text-status-warning', bgColor: 'bg-status-warning/10' }
  } else if (score >= 60) {
    return { letter: 'D', color: 'text-status-error', bgColor: 'bg-status-error/10' }
  } else {
    return { letter: 'F', color: 'text-status-error', bgColor: 'bg-status-error/10' }
  }
}

export function HealthGrade({ score, className, showLabel = true }: HealthGradeProps) {
  const { letter, color, bgColor } = getGradeFromScore(score)

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div
        className={cn(
          'relative w-24 h-24 rounded-2xl flex items-center justify-center',
          'border-2 transition-all duration-300',
          bgColor,
          letter === 'A' && 'border-status-success shadow-[0_0_20px_rgba(34,197,94,0.3)]',
          letter === 'B' && 'border-status-success/70',
          letter === 'C' && 'border-status-warning',
          letter === 'D' && 'border-status-error/70',
          letter === 'F' && 'border-status-error shadow-[0_0_20px_rgba(239,68,68,0.3)]'
        )}
      >
        <span
          className={cn(
            'text-5xl font-bold tracking-tight',
            color
          )}
        >
          {letter}
        </span>
        
        {/* Decorative ring for A grade */}
        {letter === 'A' && (
          <div className="absolute inset-0 rounded-2xl animate-pulse opacity-20 bg-status-success" />
        )}
      </div>
      
      {showLabel && (
        <div className="mt-3 text-center">
          <p className="text-sm font-medium text-foreground-secondary">
            Security Health
          </p>
          <p className={cn('text-xs mt-0.5', color)}>
            Score: {score.toFixed(1)}%
          </p>
        </div>
      )}
    </div>
  )
}

/**
 * Compact health grade for use in cards/tables
 */
export function HealthGradeBadge({ score, className }: { score: number; className?: string }) {
  const { letter, color, bgColor } = getGradeFromScore(score)

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center w-8 h-8 rounded-lg text-lg font-bold',
        bgColor,
        color,
        className
      )}
    >
      {letter}
    </span>
  )
}
