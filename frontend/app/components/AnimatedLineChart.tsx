// frontend/app/components/AnimatedLineChart.tsx
'use client'

import { useState, useEffect, useRef } from 'react'
import { Play, Pause, RotateCcw, ChevronLeft, ChevronRight } from 'lucide-react'

interface TimelineDataPoint {
  month: string // Display label (e.g., "Jan 2024")
  date?: string // Optional ISO date for sorting/reference
  total: number
  poultry: number
  dairy_cattle: number
  wild_bird: number
  wild_mammal: number
}

interface AnimatedLineChartProps {
  data?: TimelineDataPoint[]
}

export default function AnimatedLineChart({
  data = []
}: AnimatedLineChartProps) {
  const fullData = data.length > 0 ? data : []
  const [currentIndex, setCurrentIndex] = useState(
    Math.max(0, fullData.length - 1)
  )
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1000)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Reset currentIndex when data changes
  useEffect(() => {
    setCurrentIndex(Math.max(0, fullData.length - 1))
  }, [fullData.length])

  // Handle empty data
  if (fullData.length === 0) {
    return (
      <div className="bg-white p-8 rounded-lg border border-gray-200 text-center">
        <p className="text-gray-500">No timeline data available</p>
      </div>
    )
  }

  const visibleData = fullData.slice(0, currentIndex + 1)

  // Animation control
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= fullData.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, speed)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isPlaying, speed, fullData.length])

  const handleReset = () => {
    setIsPlaying(false)
    setCurrentIndex(0)
  }

  const handlePlayPause = () => {
    if (currentIndex >= fullData.length - 1) {
      setCurrentIndex(0)
    }
    setIsPlaying(!isPlaying)
  }

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsPlaying(false)
    setCurrentIndex(parseInt(e.target.value))
  }

  const handleStepForward = () => {
    setIsPlaying(false)
    setCurrentIndex((prev) => Math.min(prev + 1, fullData.length - 1))
  }

  const handleStepBackward = () => {
    setIsPlaying(false)
    setCurrentIndex((prev) => Math.max(prev - 1, 0))
  }

  const maxValue = Math.max(...fullData.map((d) => d.total)) * 1.1
  const width = 800
  const height = 400
  const padding = { top: 40, right: 120, bottom: 80, left: 60 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  const createPath = (key: keyof Omit<TimelineDataPoint, 'month' | 'date'>) => {
    if (visibleData.length === 0) return ''

    const points = visibleData.map((d, i) => {
      const x = padding.left + (i / (fullData.length - 1)) * chartWidth
      const y = padding.top + chartHeight - (d[key] / maxValue) * chartHeight
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })

    return points.join(' ')
  }

  const categories = [
    { key: 'poultry' as const, color: '#f97316', label: 'Poultry' },
    { key: 'dairy_cattle' as const, color: '#eab308', label: 'Dairy Cattle' },
    { key: 'wild_bird' as const, color: '#3b82f6', label: 'Wild Bird' },
    { key: 'wild_mammal' as const, color: '#8b5cf6', label: 'Wild Mammal' },
    { key: 'total' as const, color: '#000000', label: 'Total Cases' }
  ]

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ({
    value: Math.round(maxValue * ratio),
    y: padding.top + chartHeight - ratio * chartHeight
  }))

  return (
    <div className="space-y-4">
      <div className="relative">
        <svg
          width={width}
          height={height}
          className="border border-gray-200 rounded bg-white"
        >
          {yTicks.map((tick, i) => (
            <g key={i}>
              <line
                x1={padding.left}
                y1={tick.y}
                x2={width - padding.right}
                y2={tick.y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
              <text
                x={padding.left - 10}
                y={tick.y}
                textAnchor="end"
                alignmentBaseline="middle"
                className="text-xs fill-gray-600"
              >
                {tick.value}
              </text>
            </g>
          ))}

          {fullData.map((d, i) => {
            const x = padding.left + (i / (fullData.length - 1)) * chartWidth
            const isVisible = i <= currentIndex
            return (
              <text
                key={i}
                x={x}
                y={height - padding.bottom + 20}
                textAnchor="middle"
                className={`text-xs transition-opacity ${isVisible ? 'fill-gray-900' : 'fill-gray-300'}`}
              >
                {d.month}
              </text>
            )
          })}

          {categories.map((cat) => (
            <path
              key={cat.key}
              d={createPath(cat.key)}
              fill="none"
              stroke={cat.color}
              strokeWidth={cat.key === 'total' ? 3 : 2}
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={cat.key === 'total' ? 0.8 : 0.9}
            />
          ))}

          {visibleData.length > 0 &&
            categories.map((cat) => {
              const lastPoint = visibleData[visibleData.length - 1]
              const x =
                padding.left +
                ((visibleData.length - 1) / (fullData.length - 1)) * chartWidth
              const y =
                padding.top +
                chartHeight -
                (lastPoint[cat.key] / maxValue) * chartHeight

              return (
                <g key={`point-${cat.key}`}>
                  <circle
                    cx={x}
                    cy={y}
                    r={cat.key === 'total' ? 5 : 4}
                    fill={cat.color}
                    stroke="white"
                    strokeWidth="2"
                  />
                  <text
                    x={x + 10}
                    y={y}
                    className="text-xs font-semibold"
                    fill={cat.color}
                    alignmentBaseline="middle"
                  >
                    {lastPoint[cat.key]}
                  </text>
                </g>
              )
            })}

          {visibleData.length > 0 && (
            <line
              x1={
                padding.left +
                ((visibleData.length - 1) / (fullData.length - 1)) * chartWidth
              }
              y1={padding.top}
              x2={
                padding.left +
                ((visibleData.length - 1) / (fullData.length - 1)) * chartWidth
              }
              y2={height - padding.bottom}
              stroke="#3b82f6"
              strokeWidth="2"
              strokeDasharray="4 4"
              opacity="0.5"
            />
          )}

          <g
            transform={`translate(${width - padding.right + 20}, ${padding.top})`}
          >
            {categories.map((cat, i) => (
              <g key={cat.key} transform={`translate(0, ${i * 25})`}>
                <line
                  x1={0}
                  y1={0}
                  x2={20}
                  y2={0}
                  stroke={cat.color}
                  strokeWidth={cat.key === 'total' ? 3 : 2}
                />
                <text
                  x={25}
                  y={0}
                  alignmentBaseline="middle"
                  className="text-xs fill-gray-700"
                >
                  {cat.label}
                </text>
              </g>
            ))}
          </g>

          <text
            x={width / 2}
            y={20}
            textAnchor="middle"
            className="text-sm font-semibold fill-gray-900"
          >
            H5N1 Cases Over Time — {fullData[currentIndex].month}
          </text>
        </svg>
      </div>

      <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>{fullData[0].month}</span>
            <span className="font-semibold text-gray-900">
              {fullData[currentIndex].month} ({currentIndex + 1}/
              {fullData.length})
            </span>
            <span>{fullData[fullData.length - 1].month}</span>
          </div>

          <input
            type="range"
            min="0"
            max={fullData.length - 1}
            value={currentIndex}
            onChange={handleSliderChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={handleStepBackward}
              disabled={currentIndex === 0}
              className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              title="Previous"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <button
              onClick={handlePlayPause}
              className="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
            </button>

            <button
              onClick={handleStepForward}
              disabled={currentIndex === fullData.length - 1}
              className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              title="Next"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            <button
              onClick={handleReset}
              className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600">Speed:</label>
            <select
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value={2000}>0.5x</option>
              <option value={1000}>1x</option>
              <option value={500}>2x</option>
              <option value={250}>4x</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-3 pt-3 border-t border-gray-200">
          {categories.map((cat) => (
            <div key={cat.key} className="text-center">
              <div className="text-xs text-gray-500 mb-1">{cat.label}</div>
              <div className="text-lg font-bold" style={{ color: cat.color }}>
                {visibleData.length > 0
                  ? visibleData[visibleData.length - 1][cat.key]
                  : 0}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
