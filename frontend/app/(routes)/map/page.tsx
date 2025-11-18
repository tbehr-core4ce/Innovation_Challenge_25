'use client'
import React, { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import type {
  H5N1Case,
  HotspotZone
} from '../../components/BETSMapVisualization'
import { betsApi } from '../../../services/betsApi'

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
  const [refreshInterval, setRefreshInterval] = useState<number>(30000) // 30 seconds

  // Fetch data from API
  const fetchMapData = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await betsApi.getMapData()
      setCases(data.cases)
      setHotspots(data.hotspots)
      setLastUpdated(new Date(data.lastUpdated).toLocaleString())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
      console.error('Error fetching map data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    fetchMapData()
  }, [])

  // Auto-refresh data
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchMapData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [refreshInterval])

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
              Map View
            </h1>
            <span className="text-sm text-gray-500">
              Interactive H5N1 Case Tracking
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Last Updated: {lastUpdated}
            </div>

            <button
              onClick={fetchMapData}
              disabled={loading}
              className="text-white px-4 py-2 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: loading ? '#DAD5CB' : '#2C425A' }}
              onMouseEnter={(e) =>
                !loading && (e.currentTarget.style.backgroundColor = '#F05323')
              }
              onMouseLeave={(e) =>
                !loading && (e.currentTarget.style.backgroundColor = '#2C425A')
              }
            >
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </button>

            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="border rounded px-3 py-2 text-sm"
            >
              <option value={0}>Manual Only</option>
              <option value={15000}>15 seconds</option>
              <option value={30000}>30 seconds</option>
              <option value={60000}>1 minute</option>
              <option value={300000}>5 minutes</option>
            </select>
          </div>
        </div>
      </div>

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
