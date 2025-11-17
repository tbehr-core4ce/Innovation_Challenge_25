// frontend/app/components/PieChart.tsx

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'

interface DistributionPieChartProps {
  data: {
    name: string
    value: number
    color?: string  // Optional color field
  }[]
  title?: string
  colors?: string[]  // Fallback colors if data doesn't have colors
}

export default function DistributionPieChart({ 
  data, 
  title = "Distribution",
  colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']
}: DistributionPieChartProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color || colors[index % colors.length]} 
              />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}