'use client'

import { cn } from '@/lib/utils'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { ScoreTrend } from '@/types/dashboard'
import { TrendingUp } from 'lucide-react'

interface TrendChartProps {
  data: ScoreTrend[]
  title?: string
  className?: string
}

export function TrendChart({ data, title = '6-Month Score Trend', className }: TrendChartProps) {
  // Format data for the chart
  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short' }),
    'Secure Score': item.secure_score,
    'Compliance': item.compliance_score,
  }))

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="section-title flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-chart-primary" />
          {title}
        </h3>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#334155" 
              vertical={false}
            />
            <XAxis 
              dataKey="date" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
            />
            <YAxis 
              domain={[0, 100]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
              width={40}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1E293B',
                border: '1px solid #334155',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
              }}
              labelStyle={{ color: '#F8FAFC', marginBottom: '4px' }}
              itemStyle={{ padding: '2px 0' }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              formatter={(value) => (
                <span style={{ color: '#94A3B8', fontSize: '12px' }}>{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="Secure Score"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#3B82F6', strokeWidth: 0 }}
            />
            <Line
              type="monotone"
              dataKey="Compliance"
              stroke="#22C55E"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#22C55E', strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// Bar chart for finding age distribution
interface FindingAgeChartProps {
  data: {
    age_0_7: number
    age_7_30: number
    age_30_90: number
    age_90_plus: number
  }
  className?: string
}

export function FindingAgeChart({ data, className }: FindingAgeChartProps) {
  const chartData = [
    { name: '0-7d', count: data.age_0_7, color: '#22C55E' },
    { name: '7-30d', count: data.age_7_30, color: '#3B82F6' },
    { name: '30-90d', count: data.age_30_90, color: '#EAB308' },
    { name: '90+d', count: data.age_90_plus, color: '#EF4444' },
  ]

  const maxCount = Math.max(...chartData.map(d => d.count), 1)

  return (
    <div className={cn('card', className)}>
      <h3 className="section-title mb-4">Open Finding Age</h3>
      
      <div className="space-y-3">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-3">
            <span className="w-12 text-sm text-foreground-muted">{item.name}</span>
            <div className="flex-1 h-6 bg-background-tertiary rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${(item.count / maxCount) * 100}%`,
                  backgroundColor: item.color,
                }}
              />
            </div>
            <span className="w-8 text-sm font-medium text-foreground-primary text-right">
              {item.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
