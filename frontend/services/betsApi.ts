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
}

// Export singleton instance
export const betsApi = new BETSApiService()

// Export class for testing or custom instances
export default BETSApiService
