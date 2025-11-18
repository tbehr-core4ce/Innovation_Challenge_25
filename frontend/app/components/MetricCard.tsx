import { ReactNode } from 'react'

interface MetricCardProps {
  title: string
  value: string | number
  icon: ReactNode
  trend?: string
}

export default function MetricCard({
  title,
  value,
  icon,
  trend
}: MetricCardProps) {
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
            trend.includes('+') ? 'text-green-500' : 'text-red-500'
          }`}
        >
          {trend} from some date
        </p>
      )}
    </div>
  )
}
