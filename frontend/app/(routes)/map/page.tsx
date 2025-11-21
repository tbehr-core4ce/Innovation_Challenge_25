'use client'
import React, { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import type {
  H5N1Case,
  HotspotZone
} from '../../components/BETSMapVisualization'
import { betsApi } from '../../../services/betsApi'
import { Layers, Filter, Clock, AlertCircle } from 'lucide-react'

// Load map component dynamically (disable SSR for Leaflet)
const BETSMapVisualization = dynamic(
  () => import('@/app/components/BETSMapVisualization'),
  { ssr: false }
)

// ==================== PAGE COMPONENT ====================

export default function DashboardPage() {
  const handleCaseClick = (caseData: H5N1Case) => {
    alert(
      `Clicked: ${caseData.location}\nType: ${caseData.caseType}\nCases: ${caseData.count}`
    )
  }

  // State management
  const [cases, setCases] = useState<H5N1Case[]>([])
  const [hotspots, setHotspots] = useState<HotspotZone[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const [refreshInterval, setRefreshInterval] = useState<number>(30000)

  // Filter state
  const [timeRange, setTimeRange] = useState<number>(30) // Default 30 days
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [showLayerPanel, setShowLayerPanel] = useState<boolean>(true)

  // Layer toggles - multiple categories can be selected
  const [activeLayers, setActiveLayers] = useState<{
    poultry: boolean
    dairy_cattle: boolean
    wild_bird: boolean
    wild_mammal: boolean
    domestic_mammal: boolean
    hotspots: boolean
  }>({
    poultry: true,
    dairy_cattle: true,
    wild_bird: true,
    wild_mammal: true,
    domestic_mammal: true,
    hotspots: true
  })

  // Fetch data from API
  const fetchMapData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch data for each active layer category
      const categoryPromises = Object.entries(activeLayers)
        .filter(([key, isActive]) => isActive && key !== 'hotspots')
        .map(([category]) =>
          betsApi.getMapData({
            caseType: category,
            severity: severityFilter !== 'all' ? severityFilter : undefined,
            days: timeRange
          })
        )

      const results = await Promise.all(categoryPromises)

      // Combine all cases from different categories and deduplicate by ID
      const allCasesArray = results.flatMap((result) => result.cases)

      // Use Map to deduplicate - keeps first occurrence of each ID
      const uniqueCasesMap = new Map<string, H5N1Case>()
      allCasesArray.forEach((caseData) => {
        if (!uniqueCasesMap.has(caseData.id)) {
          uniqueCasesMap.set(caseData.id, caseData)
        }
      })
      const allCases = Array.from(uniqueCasesMap.values())

      const allHotspots =
        activeLayers.hotspots && results.length > 0
          ? results[0].hotspots
          : []

      setCases(allCases)
      setHotspots(allHotspots)
      setLastUpdated(new Date().toLocaleString())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
      console.error('Error fetching map data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Initial load and when filters change
  useEffect(() => {
    fetchMapData()
  }, [activeLayers, timeRange, severityFilter])

  // Auto-refresh data
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchMapData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [refreshInterval, activeLayers, timeRange, severityFilter])

  // Toggle individual layer
  const toggleLayer = (layer: keyof typeof activeLayers) => {
    setActiveLayers((prev) => ({
      ...prev,
      [layer]: !prev[layer]
    }))
  }

  // Loading state
  if (loading && cases.length === 0) {
    return (
      <div
        className="flex items-center justify-center w-full h-screen"
        style={{ backgroundColor: '#E4E5ED' }}
      >
        <div className="text-center">
          <div
            className="animate-spin rounded-full h-16 w-16 border-b-4 mx-auto mb-4"
            style={{ borderColor: '#F05323' }}
          ></div>
          <p className="text-lg text-gray-700">Loading BETS map data...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div
        className="flex items-center justify-center w-full h-screen"
        style={{ backgroundColor: '#E4E5ED' }}
      >
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <div className="text-red-600 text-xl font-bold mb-4">
            Error Loading Data
          </div>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={fetchMapData}
            className="text-white px-6 py-2 rounded transition"
            style={{ backgroundColor: '#2C425A' }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor = '#F05323')
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = '#2C425A')
            }
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full" style={{ height: 'calc(100vh - 0px)' }}>
      {/* Header Bar */}
      <div className="absolute top-0 left-0 right-0 z-[1001] bg-white border-b shadow-sm">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold" style={{ color: '#2C425A' }}>
              Interactive Map
            </h1>
            <span className="text-sm text-gray-500">
              H5N1 Case Tracking & Hotspot Detection
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-600" />
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
                <option value={0}>All time</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-600" />
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value="all">All Severities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <button
              onClick={() => setShowLayerPanel(!showLayerPanel)}
              className="text-white px-3 py-1 rounded transition flex items-center gap-2"
              style={{
                backgroundColor: showLayerPanel ? '#F05323' : '#2C425A'
              }}
            >
              <Layers className="w-4 h-4" />
              {showLayerPanel ? 'Hide Layers' : 'Show Layers'}
            </button>

            <div className="text-sm text-gray-600 border-l pl-4">
              Last Updated: {lastUpdated}
            </div>
          </div>
        </div>
      </div>

      {/* Layer Control Panel */}
      {showLayerPanel && (
        <div className="absolute top-20 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 w-72">
          <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
            <Layers className="w-5 h-5" style={{ color: '#2C425A' }} />
            Data Layers
          </h3>

          <div className="space-y-3">
            {/* Poultry Layer */}
            <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: '#f97316' }}
                ></div>
                <span className="text-sm font-medium">Poultry Detections</span>
              </div>
              <input
                type="checkbox"
                checked={activeLayers.poultry}
                onChange={() => toggleLayer('poultry')}
                className="w-4 h-4"
              />
            </label>

            {/* Dairy Cattle Layer */}
            <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: '#eab308' }}
                ></div>
                <span className="text-sm font-medium">
                  Dairy Cattle Detections
                </span>
              </div>
              <input
                type="checkbox"
                checked={activeLayers.dairy_cattle}
                onChange={() => toggleLayer('dairy_cattle')}
                className="w-4 h-4"
              />
            </label>

            {/* Wild Bird Layer */}
            <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: '#3b82f6' }}
                ></div>
                <span className="text-sm font-medium">Wild Bird Detections</span>
              </div>
              <input
                type="checkbox"
                checked={activeLayers.wild_bird}
                onChange={() => toggleLayer('wild_bird')}
                className="w-4 h-4"
              />
            </label>

            {/* Wild Mammal Layer */}
            <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: '#8b5cf6' }}
                ></div>
                <span className="text-sm font-medium">
                  Wild Mammal Detections
                </span>
              </div>
              <input
                type="checkbox"
                checked={activeLayers.wild_mammal}
                onChange={() => toggleLayer('wild_mammal')}
                className="w-4 h-4"
              />
            </label>

            {/* Domestic Mammal Layer */}
            <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: '#ec4899' }}
                ></div>
                <span className="text-sm font-medium">
                  Domestic Mammal Detections
                </span>
              </div>
              <input
                type="checkbox"
                checked={activeLayers.domestic_mammal}
                onChange={() => toggleLayer('domestic_mammal')}
                className="w-4 h-4"
              />
            </label>

            <div className="border-t pt-3 mt-3">
              {/* Hotspots Layer */}
              <label className="flex items-center justify-between cursor-pointer p-2 rounded hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-medium">Hotspot Zones</span>
                </div>
                <input
                  type="checkbox"
                  checked={activeLayers.hotspots}
                  onChange={() => toggleLayer('hotspots')}
                  className="w-4 h-4"
                />
              </label>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t text-xs text-gray-600">
            <p>
              <strong>{cases.length}</strong> cases displayed
            </p>
            <p>
              <strong>{hotspots.length}</strong> hotspot zones detected
            </p>
          </div>
        </div>
      )}

      <div className="w-full h-screen">
        <BETSMapVisualization
          cases={cases}
          hotspots={hotspots}
          center={[39.8283, -98.5795]}
          zoom={5}
          onCaseClick={handleCaseClick}
        />
      </div>

      {/* Loading Overlay */}
      {loading && cases.length > 0 && (
        <div
          className="absolute top-20 right-4 z-[1001] text-white px-4 py-2 rounded shadow-lg"
          style={{ backgroundColor: '#F05323' }}
        >
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-sm">Updating...</span>
          </div>
        </div>
      )}
    </div>
  )
}
