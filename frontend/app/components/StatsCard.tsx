// frontend/app/components/StatsCard.tsx
import { ReactNode } from 'react'

interface StatsCardProps {
  title: string
  value: string | number
  icon: ReactNode
  bgColor?: string
  textColor?: string
}

export default function StatsCard({ 
  title, 
  value, 
  icon,
  bgColor = 'bg-green-50',
  textColor = 'text-green-700'
}: StatsCardProps) {
  return (
    <div className={`${bgColor} border border-opacity-20 rounded-lg p-4`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm ${textColor} font-medium`}>{title}</p>
          <p className={`text-2xl font-bold ${textColor.replace('700', '900')}`}>
            {value}
          </p>
        </div>
        <div className={`w-12 h-12 ${bgColor.replace('50', '200')} rounded-full flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </div>
  )
}