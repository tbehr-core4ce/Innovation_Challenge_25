'use client'

// frontend/app/(routes)/dashboard/page.tsx
// Dashboard based on YOUR actual H5N1Case database model

import { useState, useEffect } from 'react'
import { Map, Activity, AlertTriangle, Users, Bird, TrendingUp } from 'lucide-react'
import MetricCard from '@/app/components/MetricCard'
import BarChart from '@/app/components/BarChart'
import LineChart from '@/app/components/LineChart'
import PieChart from '@/app/components/PieChart'
import Tooltip from '@/app/components/Tooltip'

// ==================== DATA TYPES (Based on YOUR models.py) ====================

interface AnalyticsData {
  totalCases: number
  confirmedCases: number
  suspectedCases: number
  underInvestigation: number
  criticalSeverity: number
  highSeverity: number
  animalsAffected: number
  animalsDeceased: number
}

interface TimelineDataPoint {
  month: string
  total: number
  poultry: number
  dairy_cattle: number
  wild_bird: number
  wild_mammal: number
}

interface RegionDataPoint {
  name: string
  value: number
}

interface AnimalCategoryData {
  name: string
  value: number
  color: string
}

interface StatusData {
  name: string
  value: number
  color: string
}

interface DataSourceData {
  name: string
  value: number
}

interface RecentAlert {
  date: string
  type: string
  location: string
  severity: string
  message: string
}

//  DATA FETCHER 

async function fetchDashboardData() {
  
  return {
    analytics: {
      totalCases: 247,
      confirmedCases: 189,
      suspectedCases: 34,
      underInvestigation: 24,
      criticalSeverity: 8,
      highSeverity: 34,
      animalsAffected: 12450,
      animalsDeceased: 3890
    },
    timeline: [
      { month: 'Jan', total: 45, poultry: 38, dairy_cattle: 5, wild_bird: 2, wild_mammal: 0 },
      { month: 'Feb', total: 62, poultry: 52, dairy_cattle: 7, wild_bird: 3, wild_mammal: 0 },
      { month: 'Mar', total: 78, poultry: 65, dairy_cattle: 8, wild_bird: 4, wild_mammal: 1 },
      { month: 'Apr', total: 95, poultry: 79, dairy_cattle: 10, wild_bird: 5, wild_mammal: 1 },
      { month: 'May', total: 134, poultry: 112, dairy_cattle: 14, wild_bird: 6, wild_mammal: 2 },
      { month: 'Jun', total: 189, poultry: 165, dairy_cattle: 14, wild_bird: 8, wild_mammal: 2 },
      { month: 'Jul', total: 247, poultry: 189, dairy_cattle: 46, wild_bird: 10, wild_mammal: 2 }
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
}

//  MAIN DASHBOARD 

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [timelineData, setTimelineData] = useState<TimelineDataPoint[]>([])
  const [regionData, setRegionData] = useState<RegionDataPoint[]>([])
  const [animalCategories, setAnimalCategories] = useState<AnimalCategoryData[]>([])
  const [statusData, setStatusData] = useState<StatusData[]>([])
  const [dataSources, setDataSources] = useState<DataSourceData[]>([])
  const [recentAlerts, setRecentAlerts] = useState<RecentAlert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const data = await fetchDashboardData()
      
      setAnalytics(data.analytics)
      setTimelineData(data.timeline)
      setRegionData(data.regions)
      setAnimalCategories(data.animalCategories)
      setStatusData(data.statusBreakdown)
      setDataSources(data.dataSources)
      setRecentAlerts(data.recentAlerts)
      setLoading(false)
    }

    loadData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!analytics) return null

  const mortalityRate = ((analytics.animalsDeceased / analytics.animalsAffected) * 100).toFixed(1)

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* HEADER */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                H5N1 Surveillance Dashboard
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Real-time Monitoring and Surveillance  
              </p>
            </div>
              <a 
                href="/map" 
                className="px-3 py- bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
              >
                <Map className="w-5 h-5" />
                View Map
              </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">

        {/*  KEY METRICS  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <Tooltip content="Total number of reported H5N1 cases across all species">
              <MetricCard
                title="Total Cases"
                value={analytics.totalCases.toLocaleString()}
                icon={<Activity className="text-blue-500 w-6 h-6" />}
                trend="+12.5%"
              />
            </Tooltip>
            
            <Tooltip content="Cases confirmed through lab testing or official reporting">
              <MetricCard
                title="Confirmed Cases"
                value={analytics.confirmedCases.toLocaleString()}
                icon={<AlertTriangle className="text-green-500 w-6 h-6" />}
                trend={`${((analytics.confirmedCases/analytics.totalCases)*100).toFixed(0)}% of total`}
              />
            </Tooltip>
            
            <Tooltip content="Number of cases classified as high or critical severity">
              <MetricCard
                title="High/Critical Severity"
                value={(analytics.highSeverity + analytics.criticalSeverity).toLocaleString()}
                icon={<AlertTriangle className="text-red-500 w-6 h-6" />}
                trend={`${analytics.criticalSeverity} critical`}
              />
            </Tooltip>
            
            <Tooltip content="Total number of animals affected by H5N1">
              <MetricCard
                title="Animals Affected"
                value={analytics.animalsAffected.toLocaleString()}
                icon={<Bird className="text-orange-500 w-6 h-6" />}
                trend={`${mortalityRate}% mortality`}
              />
            </Tooltip>
          </div>
        </section>

        {/*  TREND ANALYSIS  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Trend Analysis</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* LINE CHART */}
            <Tooltip content="Monthly case trends by animal category">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Cases Over Time/Animal Category (Could animate this (?))</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Monthly breakdown by WOAH animal categories
                </p>
                <LineChart data={timelineData} />
              </div>
            </Tooltip>

            {/* PIE CHART - Animal Categories */}
            <Tooltip content="Proportion of cases by WOAH animal categories">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Animal Category Distribution</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Breakdown by WOAH categories
                </p>
                <PieChart data={animalCategories} />
              </div>
            </Tooltip>
          </div>
        </section>

        {/* STATUS & DATA SOURCES  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Case Status & Data Sources</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Status Breakdown */}
            <Tooltip content="Current investigation status of all cases">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Case Status</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Current investigation status
                </p>
                <PieChart data={statusData} />
              </div>
            </Tooltip>

            {/* Data Sources */}
            <Tooltip content="Breakdown of reporting sources for all cases">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Data Sources</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Cases by reporting organization
                </p>
                <BarChart data={dataSources} />
              </div>
            </Tooltip>
          </div>
        </section>

        {/*  REGIONAL BREAKDOWN  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Regional Breakdown</h2>
          <BarChart data={regionData} />
        </section>

        {/*  RECENT ALERTS  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Alerts</h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 divide-y divide-gray-200">
            {recentAlerts.map((alert, index) => (
              <Tooltip key={index} content={alert.message}>
                <div className="p-4 hover:bg-gray-50 transition">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`mt-1 w-2 h-2 rounded-full ${
                        alert.severity === 'high' ? 'bg-red-500' : 
                        alert.severity === 'medium' ? 'bg-yellow-500' : 
                        'bg-blue-500'
                      }`}></div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">{alert.type}</span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-600">{alert.location}</span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                      {alert.date}
                    </span>
                  </div>
                </div>
              </Tooltip>
            ))}
          </div>
        </section>

        {/*  SEVERITY SUMMARY  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Severity Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            <Tooltip content="Number of cases classified as critical severity">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-red-700 font-medium uppercase tracking-wide">
                      Critical
                    </p>
                    <p className="text-3xl font-bold text-red-900 mt-2">
                      {analytics.criticalSeverity}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-red-200 rounded-full flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-red-700" />
                  </div>
                </div>
              </div>
            </Tooltip>

            <Tooltip content="Number of cases classified as high severity">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-orange-700 font-medium uppercase tracking-wide">
                      High
                    </p>
                    <p className="text-3xl font-bold text-orange-900 mt-2">
                      {analytics.highSeverity}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-orange-200 rounded-full flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-orange-700" />
                  </div>
                </div>
              </div>
            </Tooltip>

            <Tooltip content="Cases currently under investigation">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-yellow-700 font-medium uppercase tracking-wide">
                      Under Investigation
                    </p>
                    <p className="text-3xl font-bold text-yellow-900 mt-2">
                      {analytics.underInvestigation}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-200 rounded-full flex items-center justify-center">
                    <Activity className="w-6 h-6 text-yellow-700" />
                  </div>
                </div>
              </div>
            </Tooltip>

            <Tooltip content="Cases classified as suspected">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-700 font-medium uppercase tracking-wide">
                      Suspected
                    </p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {analytics.suspectedCases}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-200 rounded-full flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-blue-700" />
                  </div>
                </div>
              </div>
            </Tooltip>
          </div>
        </section>

        {/* INFO BOX */}
        <Tooltip content="Dashboard status info and last updated timestamp">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Activity className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">
                  Dashboard Status
                </h4>
               <p className="text-sm text-blue-700">
  all this data is fake :c for now
  Last updated: {new Date().toLocaleString()}
</p>
   </div> 
            </div> 
          </div> 
        </Tooltip>
      </div> 
    </div> 
  )
}