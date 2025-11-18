/**
 * BETS API Service
 * React service for fetching H5N1 case data from FastAPI backend
 */

import { H5N1Case, HotspotZone } from '../app/components/BETSMapVisualization'

const API_BASE_URL =
  process.env.NEXT_PUBLIC_PYTHON_API_URL ||
  process.env.PYTHON_API_URL ||
  'http://localhost:8000'

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

    if (filters?.caseType) params.append('category', filters.caseType)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.days) params.append('days', filters.days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<{
      cases: Array<{
        id: string
        lat: number
        lng: number
        location: string
        caseType: string
        count: number
        severity: string
        reportedDate: string
        status: string
        description?: string
      }>
      hotspots: HotspotZone[]
    }>(`/api/map-data${queryString}`)

    // Map backend animal categories to frontend case types
    const categoryMap: Record<string, H5N1Case['caseType']> = {
      poultry: 'avian',
      wild_bird: 'avian',
      dairy_cattle: 'dairy',
      wild_mammal: 'environmental',
      domestic_mammal: 'environmental',
      other: 'environmental',
      human: 'human'
    }

    // Transform cases to match frontend expectations
    const transformedCases: H5N1Case[] = response.cases.map((c) => ({
      ...c,
      caseType:
        categoryMap[c.caseType] ||
        ('environmental' as H5N1Case['caseType']),
      severity: c.severity as H5N1Case['severity'],
      status: c.status as H5N1Case['status']
    }))

    return {
      cases: transformedCases,
      hotspots: response.hotspots,
      lastUpdated: new Date().toISOString()
    }
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

  /**
   * Get dashboard overview metrics
   * Backend endpoint: GET /api/dashboard/overview
   */
  async getDashboardOverview(days: number = 90): Promise<AnalyticsData> {
    const params = new URLSearchParams()
    if (days > 0) params.append('days', days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<{
      totalCases: number
      confirmedCases: number
      suspectedCases: number
      underInvestigation: number
      criticalCases: number
      highSeverityCases: number
      totalAnimalsAffected: number
      totalAnimalsDeceased: number
    }>(`/api/dashboard/overview${queryString}`)

    // Transform backend response to match frontend expectations
    return {
      totalCases: response.totalCases,
      confirmedCases: response.confirmedCases,
      suspectedCases: response.suspectedCases,
      underInvestigation: response.underInvestigation,
      criticalSeverity: response.criticalCases,
      highSeverity: response.highSeverityCases,
      animalsAffected: response.totalAnimalsAffected,
      animalsDeceased: response.totalAnimalsDeceased,
      lastUpdated: new Date().toISOString()
    }
  }

  /**
   * Get timeline data
   * Backend endpoint: GET /api/dashboard/timeline
   */
  async getDashboardTimeline(
    months: number = 12
  ): Promise<TimelineDataPoint[]> {
    const params = new URLSearchParams()
    if (months) params.append('months', months.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    return this.fetchApi<TimelineDataPoint[]>(
      `/api/dashboard/timeline${queryString}`
    )
  }

  /**
   * Get regional breakdown
   * Backend endpoint: GET /api/dashboard/regions
   */
  async getDashboardRegions(
    days: number = 90,
    limit: number = 10
  ): Promise<RegionDataPoint[]> {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())
    if (limit) params.append('limit', limit.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<
      { region: string; caseCount: number }[]
    >(`/api/dashboard/regions${queryString}`)

    // Transform backend response to match frontend expectations
    return response.map((item) => ({
      name: item.region,
      value: item.caseCount
    }))
  }

  /**
   * Get animal category distribution
   * Backend endpoint: GET /api/dashboard/animal-categories
   */
  async getAnimalCategories(days: number = 90): Promise<AnimalCategoryData[]> {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<
      { category: string; count: number; color: string }[]
    >(`/api/dashboard/animal-categories${queryString}`)

    // Transform backend response to match frontend expectations
    return response.map((item) => ({
      name: item.category,
      value: item.count,
      color: item.color
    }))
  }

  /**
   * Get case status breakdown
   * Backend endpoint: GET /api/dashboard/status
   */
  async getStatusBreakdown(days: number = 90): Promise<StatusData[]> {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<{ status: string; count: number }[]>(
      `/api/dashboard/status${queryString}`
    )

    // Define colors for different statuses
    const statusColors: Record<string, string> = {
      confirmed: '#10b981',
      suspected: '#f59e0b',
      under_investigation: '#3b82f6',
      negative: '#6b7280',
      inconclusive: '#8b5cf6'
    }

    // Transform backend response to match frontend expectations
    return response
      .filter((item) => item && item.status) // Filter out any invalid items
      .map((item) => {
        const status = item.status.toLowerCase()
        // Convert status to readable name
        const name = status
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')

        return {
          name,
          value: item.count,
          color: statusColors[status] || '#6b7280'
        }
      })
  }

  /**
   * Get data sources
   * Backend endpoint: GET /api/dashboard/sources
   */
  async getDataSources(days: number = 90): Promise<DataSourceData[]> {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<{ source: string; count: number }[]>(
      `/api/dashboard/sources${queryString}`
    )

    // Transform backend response to match frontend expectations
    return response.map((item) => ({
      name: item.source,
      value: item.count
    }))
  }

  /**
   * Get recent alerts
   * Backend endpoint: GET /api/alerts/recent
   */
  async getDashboardAlerts(
    days: number = 30,
    limit: number = 10
  ): Promise<RecentAlert[]> {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())
    if (limit) params.append('limit', limit.toString())

    const queryString = params.toString() ? `?${params.toString()}` : ''
    const response = await this.fetchApi<
      {
        id: string
        type: string
        severity: string
        title: string
        message: string
        location: string
        date: string
        caseCount: number
      }[]
    >(`/api/alerts/recent${queryString}`)

    // Transform backend response to match frontend expectations
    return response.map((item) => ({
      date: new Date(item.date).toLocaleDateString(),
      type: item.title,
      location: item.location,
      severity: item.severity,
      message: item.message
    }))
  }
}

// Export singleton instance
export const betsApi = new BETSApiService()

// Export class for testing or custom instances
export default BETSApiService
