// frontend/app/components/MetricCard.tsx
import { ReactNode } from 'react'

interface MetricCardProps {
  title: string
  value: string | number
  icon: ReactNode
  trend?: string
  timeRange?: number // Add this prop
}

export default function MetricCard({
  title,
  value,
  icon,
  trend,
  timeRange
}: MetricCardProps) {
  // Calculate the date range text
  const getDateRangeText = () => {
    if (!timeRange || timeRange === 0) {
      return 'all time'
    }
    
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - timeRange)
    
    return `since ${startDate.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: startDate.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    })}`
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold">{value}</h3>
        </div>
        <div className="p-3 bg-blue-50 rounded-full">{icon}</div>
      </div>
      {trend && (
        <p
          className={`text-xs mt-2 ${
            trend.includes('+') ? 'text-green-500' : 'text-gray-500'
          }`}
        >
          {trend} {getDateRangeText()}
        </p>
      )}
    </div>
  )
}