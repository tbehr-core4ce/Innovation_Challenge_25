/**
 * BETS API Service
 * React service for fetching H5N1 case data from FastAPI backend
 */

import { H5N1Case, HotspotZone } from '../app/components/BETSMapVisualization'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// ==================== TYPE DEFINITIONS ====================

interface MapDataResponse {
  cases: H5N1Case[]
  hotspots: HotspotZone[]
  lastUpdated: string
}

interface StatsResponse {
  totalCases: number
  humanCases: number
  avianCases: number
  dairyCases: number
  environmentalCases: number
  criticalCases: number
  activeCases: number
  lastUpdated: string
}

interface Alert {
  level: 'critical' | 'warning' | 'info'
  message: string
  timestamp: string
}

interface ApiError {
  detail: string
}

export interface AnalyticsData {
  totalCases: number
  confirmedCases: number
  suspectedCases: number
  underInvestigation: number
  criticalSeverity: number
  highSeverity: number
  animalsAffected: number
  animalsDeceased: number
  lastUpdated: string
}

export interface TimelineDataPoint {
  month: string
  total: number
  poultry: number
  dairy_cattle: number
  wild_bird: number
  wild_mammal: number
}

export interface RegionDataPoint {
  name: string
  value: number
}

export interface AnimalCategoryData {
  name: string
  value: number
  color: string
}

export interface StatusData {
  name: string
  value: number
  color: string
}

export interface DataSourceData {
  name: string
  value: number
}

export interface RecentAlert {
  date: string
  type: string
  location: string
  severity: string
  message: string
}

// TODO: Remove this section when backend APIs are ready (?) and then make sure API is working correctly

const MOCK_DASHBOARD_DATA = {
  overview: {
    totalCases: 247,
    confirmedCases: 189,
    suspectedCases: 34,
    underInvestigation: 24,
    criticalSeverity: 8,
    highSeverity: 34,
    animalsAffected: 12450,
    animalsDeceased: 3890,
    lastUpdated: new Date().toISOString()
  },

  timeline: [
    {
      month: 'Jan',
      total: 45,
      poultry: 38,
      dairy_cattle: 5,
      wild_bird: 2,
      wild_mammal: 0
    },
    {
      month: 'Feb',
      total: 62,
      poultry: 52,
      dairy_cattle: 7,
      wild_bird: 3,
      wild_mammal: 0
    },
    {
      month: 'Mar',
      total: 78,
      poultry: 65,
      dairy_cattle: 8,
      wild_bird: 4,
      wild_mammal: 1
    },
    {
      month: 'Apr',
      total: 95,
      poultry: 79,
      dairy_cattle: 10,
      wild_bird: 5,
      wild_mammal: 1
    },
    {
      month: 'May',
      total: 134,
      poultry: 112,
      dairy_cattle: 14,
      wild_bird: 6,
      wild_mammal: 2
    },
    {
      month: 'Jun',
      total: 189,
      poultry: 165,
      dairy_cattle: 14,
      wild_bird: 8,
      wild_mammal: 2
    },
    {
      month: 'Jul',
      total: 247,
      poultry: 189,
      dairy_cattle: 46,
      wild_bird: 10,
      wild_mammal: 2
    }
  ],

  regions: [
    { name: 'California', value: 45 },
    { name: 'Texas', value: 38 },
    { name: 'Michigan', value: 32 },
    { name: 'Wisconsin', value: 28 },
    { name: 'New York', value: 24 },
    { name: 'Florida', value: 21 },
    { name: 'Others', value: 59 }
  ],

  animalCategories: [
    { name: 'Poultry', value: 189, color: '#f97316' },
    { name: 'Dairy Cattle', value: 46, color: '#eab308' },
    { name: 'Wild Bird', value: 10, color: '#3b82f6' },
    { name: 'Wild Mammal', value: 2, color: '#8b5cf6' }
  ],

  statusBreakdown: [
    { name: 'Confirmed', value: 189, color: '#10b981' },
    { name: 'Suspected', value: 34, color: '#f59e0b' },
    { name: 'Under Investigation', value: 24, color: '#3b82f6' }
  ],

  dataSources: [
    { name: 'WOAH', value: 120 },
    { name: 'CDC', value: 45 },
    { name: 'USDA', value: 67 },
    { name: 'State Agency', value: 15 }
  ],

  recentAlerts: [
    {
      date: '2024-07-15',
      type: 'New Outbreak',
      location: 'California',
      severity: 'high',
      message: 'Cluster detected in dairy farms'
    },
    {
      date: '2024-07-14',
      type: 'Geographic Spread',
      location: 'Texas',
      severity: 'medium',
      message: 'Cases spreading to neighboring counties'
    },
    {
      date: '2024-07-13',
      type: 'Severity Increase',
      location: 'Michigan',
      severity: 'high',
      message: 'Multiple high-severity cases reported'
    }
  ]
}

// Mock delay to simulate network request
const mockDelay = () => new Promise((resolve) => setTimeout(resolve, 500))

// ==================== API CLIENT ====================

class BETSApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async fetchApi<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers
        }
      })

      if (!response.ok) {
        const error: ApiError = await response.json()
        throw new Error(error.detail || `API Error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`Failed to fetch ${endpoint}:`, error)
      throw error
    }
  }

  /**
   * Get all map data (cases + hotspots)
   */
  async getMapData(filters?: {
    caseType?: string
    severity?: string
    days?: number
  }): Promise<MapDataResponse> {
    const params = new URLSearchParams()

    if (filters?.caseType) params.append('case_type', filters.caseType)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.days) params.append('days', filters.days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    return this.fetchApi<MapDataResponse>(`/api/map-data${queryString}`)
  }

  /**
   * Get filtered H5N1 cases
   */
  async getCases(filters?: {
    caseType?: string
    severity?: string
    status?: string
  }): Promise<H5N1Case[]> {
    const params = new URLSearchParams()

    if (filters?.caseType) params.append('case_type', filters.caseType)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.status) params.append('status', filters.status)

    const queryString = params.toString() ? `?${params.toString()}` : ''
    return this.fetchApi<H5N1Case[]>(`/api/cases${queryString}`)
  }

  /**
   * Get hotspot zones
   */
  async getHotspots(minRiskLevel?: string): Promise<HotspotZone[]> {
    const params = new URLSearchParams()
    if (minRiskLevel) params.append('min_risk_level', minRiskLevel)

    const queryString = params.toString() ? `?${params.toString()}` : ''
    return this.fetchApi<HotspotZone[]>(`/api/hotspots${queryString}`)
  }

  /**
   * Get aggregate statistics
   */
  async getStats(): Promise<StatsResponse> {
    return this.fetchApi<StatsResponse>('/api/stats')
  }

  /**
   * Get active alerts
   */
  async getAlerts(): Promise<Alert[]> {
    return this.fetchApi<Alert[]>('/api/alerts')
  }

  /**
   * Report a new case
   */
  async reportCase(
    caseData: H5N1Case
  ): Promise<{ message: string; id: string }> {
    return this.fetchApi('/api/cases', {
      method: 'POST',
      body: JSON.stringify(caseData)
    })
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.fetchApi('/health')
  }

  //  DASHBOARD API ENDPOINTS
  //  TODO: Make sure these endpoints make sense

  /**
   * Get dashboard overview metrics
   * Backend endpoint: GET /api/dashboard/overview
   */
  async getDashboardOverview() {
    // TODO: Replace with real API call
    await mockDelay()
    return MOCK_DASHBOARD_DATA.overview

    // TODO: When backend is ready, uncomment this:
    // return this.fetchApi('/api/dashboard/overview')
  }

  /**
   * Get timeline data
   * Backend endpoint: GET /api/dashboard/timeline
   */
  async getDashboardTimeline() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.timeline

    // TODO: When backend is ready:
    // return this.fetchApi('/api/dashboard/timeline')
  }

  /**
   * Get regional breakdown
   * Backend endpoint: GET /api/dashboard/regions
   */
  async getDashboardRegions() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.regions

    // TODO: When backend is ready:
    // return this.fetchApi('/api/dashboard/regions')
  }

  /**
   * Get animal category distribution
   * Backend endpoint: GET /api/dashboard/animal-categories
   */
  async getAnimalCategories() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.animalCategories

    // TODO: When backend is ready:
    // return this.fetchApi('/api/dashboard/animal-categories')
  }

  /**
   * Get case status breakdown
   * Backend endpoint: GET /api/dashboard/status
   */
  async getStatusBreakdown() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.statusBreakdown

    // TODO: When backend is ready:
    // return this.fetchApi('/api/dashboard/status')
  }

  /**
   * Get data sources
   * Backend endpoint: GET /api/dashboard/sources
   */
  async getDataSources() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.dataSources

    // TODO: When backend is ready:
    // return this.fetchApi('/api/dashboard/sources')
  }

  /**
   * Get recent alerts
   * Backend endpoint: GET /api/alerts/recent
   */
  async getDashboardAlerts() {
    await mockDelay()
    return MOCK_DASHBOARD_DATA.recentAlerts

    // TODO: When backend is ready:
    // return this.fetchApi('/api/alerts/recent')
  }
}

// Export singleton instance
export const betsApi = new BETSApiService()

// Export class for testing or custom instances
export default BETSApiService
