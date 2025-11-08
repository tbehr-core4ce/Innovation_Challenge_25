import React from 'react'
import BETSMapVisualization, {
  H5N1Case,
  HotspotZone
} from '../../components/BETSMapVisualization'

// ==================== MOCK DATA ====================

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

export default function DashboardPage() {
  const handleCaseClick = (caseData: H5N1Case) => {
    console.log('Case clicked:', caseData)
    // You could open a detailed modal, update a side panel, etc.
    alert(
      `Clicked: ${caseData.location}\nType: ${caseData.caseType}\nCases: ${caseData.count}`
    )

    return (
      <div className="w-full h-screen">
        <BETSMapVisualization
          cases={mockCases}
          hotspots={mockHotspots}
          center={[39.8283, -98.5795]} // Center of USA
          zoom={5}
          onCaseClick={handleCaseClick}
        />
      </div>
    )
  }
}
