// src/components/BarChart.tsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer
} from 'recharts'

interface BarChartProps {
  data: {
    name: string
    value: number
  }[]
}

export default function AnalyticsBarChart({ data }: BarChartProps) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="font-medium mb-4">Case Overview</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" />
          <YAxis />
          <Bar dataKey="value" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
