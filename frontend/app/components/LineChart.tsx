// frontend/app/components/LineChart.tsx

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'

interface TimelineChartProps {
  data: {
    month: string
    total: number
    poultry: number
    dairy_cattle: number
    wild_bird: number
    wild_mammal: number
  }[]
  title?: string
}

export default function TimelineChart({
  data,
  title = 'Case Timeline'
}: TimelineChartProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#6b7280" />
          <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="total"
            stroke="#3b82f6"
            strokeWidth={3}
            name="Total Cases"
          />
          <Line
            type="monotone"
            dataKey="poultry"
            stroke="#f97316"
            strokeWidth={2}
            name="Poultry"
          />
          <Line
            type="monotone"
            dataKey="dairy_cattle"
            stroke="#eab308"
            strokeWidth={2}
            name="Dairy Cattle"
          />
          <Line
            type="monotone"
            dataKey="wild_bird"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Wild Bird"
          />
          <Line
            type="monotone"
            dataKey="wild_mammal"
            stroke="#8b5cf6"
            strokeWidth={2}
            name="Wild Mammal"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
