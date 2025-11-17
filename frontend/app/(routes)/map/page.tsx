'use client'
import React, { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import type {
  H5N1Case,
  HotspotZone
} from '../../components/BETSMapVisualization'
import { betsApi } from '../../../services/betsApi'

// ==================== MOCK DATA ====================
const BETSMapVisualization = dynamic(
  () => import('@/app/components/BETSMapVisualization'),
  { ssr: false } // disable SSR for Leaflet
)

const mockCases: H5N1Case[] = [
  // California Dairy Cases
  {
    id: '1',
    lat: 36.7783,
    lng: -119.4179,
    location: 'Tulare County, CA',
    caseType: 'dairy',
    count: 15,
    severity: 'high',
    reportedDate: '2025-11-05',
    status: 'monitoring',
    description:
      'Dairy cattle herd showing symptoms. Quarantine measures in place.'
  },
  {
    id: '2',
    lat: 37.6391,
    lng: -120.997,
    location: 'Merced County, CA',
    caseType: 'dairy',
    count: 8,
    severity: 'medium',
    reportedDate: '2025-11-04',
    status: 'contained'
  },

  // Human Cases
  {
    id: '3',
    lat: 36.7477,
    lng: -119.7871,
    location: 'Fresno, CA',
    caseType: 'human',
    count: 2,
    severity: 'critical',
    reportedDate: '2025-11-06',
    status: 'active',
    description:
      'Two dairy workers tested positive. Hospitalized and receiving treatment.'
  },
  {
    id: '4',
    lat: 39.7392,
    lng: -104.9903,
    location: 'Denver, CO',
    caseType: 'human',
    count: 1,
    severity: 'high',
    reportedDate: '2025-11-03',
    status: 'monitoring',
    description: 'Poultry worker exposed. Currently isolated.'
  },

  // Avian Cases
  {
    id: '5',
    lat: 40.7128,
    lng: -74.006,
    location: 'New York, NY',
    caseType: 'avian',
    count: 45,
    severity: 'medium',
    reportedDate: '2025-11-01',
    status: 'contained',
    description: 'Wild bird population affected in Central Park area.'
  },
  {
    id: '6',
    lat: 41.8781,
    lng: -87.6298,
    location: 'Chicago, IL',
    caseType: 'avian',
    count: 32,
    severity: 'high',
    reportedDate: '2025-10-30',
    status: 'monitoring'
  },
  {
    id: '7',
    lat: 47.6062,
    lng: -122.3321,
    location: 'Seattle, WA',
    caseType: 'avian',
    count: 67,
    severity: 'critical',
    reportedDate: '2025-11-05',
    status: 'active',
    description: 'Major outbreak in commercial poultry facilities.'
  },

  // Environmental Cases
  {
    id: '8',
    lat: 29.7604,
    lng: -95.3698,
    location: 'Houston, TX',
    caseType: 'environmental',
    count: 3,
    severity: 'low',
    reportedDate: '2025-10-28',
    status: 'monitoring',
    description: 'Virus detected in wastewater sampling.'
  },
  {
    id: '9',
    lat: 33.4484,
    lng: -112.074,
    location: 'Phoenix, AZ',
    caseType: 'environmental',
    count: 2,
    severity: 'low',
    reportedDate: '2025-10-25',
    status: 'monitoring'
  },

  // Additional Cases for clustering demo
  {
    id: '10',
    lat: 36.8,
    lng: -119.5,
    location: 'Fresno County, CA',
    caseType: 'dairy',
    count: 12,
    severity: 'high',
    reportedDate: '2025-11-04',
    status: 'active'
  },
  {
    id: '11',
    lat: 36.85,
    lng: -119.6,
    location: 'Kings County, CA',
    caseType: 'dairy',
    count: 9,
    severity: 'medium',
    reportedDate: '2025-11-03',
    status: 'monitoring'
  },
  {
    id: '12',
    lat: 36.9,
    lng: -119.55,
    location: 'Madera County, CA',
    caseType: 'dairy',
    count: 6,
    severity: 'medium',
    reportedDate: '2025-11-02',
    status: 'contained'
  }
]

const mockHotspots: HotspotZone[] = [
  {
    id: 'h1',
    lat: 36.8,
    lng: -119.5,
    radius: 50000, // 50km
    caseCount: 42,
    riskLevel: 'critical'
  },
  {
    id: 'h2',
    lat: 47.6062,
    lng: -122.3321,
    radius: 30000, // 30km
    caseCount: 67,
    riskLevel: 'critical'
  },
  {
    id: 'h3',
    lat: 41.8781,
    lng: -87.6298,
    radius: 40000, // 40km
    caseCount: 32,
    riskLevel: 'high'
  },
  {
    id: 'h4',
    lat: 40.7128,
    lng: -74.006,
    radius: 25000, // 25km
    caseCount: 45,
    riskLevel: 'medium'
  }
]

// ==================== EXAMPLE USAGE ====================

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
      <div className="flex items-center justify-center w-full h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-700">Loading BETS data...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-gray-100">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <div className="text-red-600 text-xl font-bold mb-4">
            Error Loading Data
          </div>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={fetchMapData}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-screen">
      {/* Header Bar */}
      <div className="absolute top-0 left-0 right-0 z-[1001] bg-white border-b shadow-sm">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-800">
              BETS - Bio-Event Tracking System
            </h1>
            <span className="text-sm text-gray-500">
              H5N1 Surveillance Dashboard
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Last Updated: {lastUpdated}
            </div>

            <button
              onClick={fetchMapData}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
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
          cases={mockCases}
          hotspots={mockHotspots}
          center={[39.8283, -98.5795]}
          zoom={5}
          onCaseClick={handleCaseClick}
        />
      </div>

      {/* Loading Overlay */}
      {loading && cases.length > 0 && (
        <div className="absolute top-20 right-4 z-[1001] bg-blue-600 text-white px-4 py-2 rounded shadow-lg">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-sm">Updating...</span>
          </div>
        </div>
      )}
    </div>
  )
}
