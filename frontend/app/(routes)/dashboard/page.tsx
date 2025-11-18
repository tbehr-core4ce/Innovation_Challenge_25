'use client'
// TODO: Add error boundary component in frontend/components to handle API failures and display user-friendly error messages
// TODO: Implement dark/light toggle mode to address the usability aspect of this project, not a high priority task though
// TODO: Add accessibility and usability improvements, without clunking up user interface, not a high priority
// TODO: Add tooltips with more detailed information for user interface components that make sense to have them
// TODO: Either replace existing timeline chart with an animated one where you can have a slider to animate case progression over time in reason of data
// TODO: If possible, add filtering and search options either on dashboard or
// TODO: Add real-time notifications/alerts when new critical cases are detected

// frontend/app/(routes)/dashboard/page.tsx
import { useState, useEffect } from 'react'
import {
  Map,
  Activity,
  AlertTriangle,
  Users,
  Bird,
  TrendingUp
} from 'lucide-react'
import {
  betsApi,
  AnalyticsData,
  TimelineDataPoint,
  RegionDataPoint,
  AnimalCategoryData,
  StatusData,
  DataSourceData,
  RecentAlert
} from '@/services/betsApi'
import MetricCard from '@/app/components/MetricCard'
import BarChart from '@/app/components/BarChart'
import LineChart from '@/app/components/LineChart'
import PieChart from '@/app/components/PieChart'
import Tooltip from '@/app/components/Tooltip'

//  MAIN DASHBOARD

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [timelineData, setTimelineData] = useState<TimelineDataPoint[]>([])
  const [regionData, setRegionData] = useState<RegionDataPoint[]>([])
  const [animalCategories, setAnimalCategories] = useState<
    AnimalCategoryData[]
  >([])
  const [statusData, setStatusData] = useState<StatusData[]>([])
  const [dataSources, setDataSources] = useState<DataSourceData[]>([])
  const [recentAlerts, setRecentAlerts] = useState<RecentAlert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)

      try {
        // Fetch all data from API
        const [overview, timeline, regions, animals, status, sources, alerts] =
          await Promise.all([
            betsApi.getDashboardOverview(),
            betsApi.getDashboardTimeline(),
            betsApi.getDashboardRegions(),
            betsApi.getAnimalCategories(),
            betsApi.getStatusBreakdown(),
            betsApi.getDataSources(),
            betsApi.getDashboardAlerts()
          ])

        // Update state with API data
        setAnalytics(overview)
        setTimelineData(timeline)
        setRegionData(regions)
        setAnimalCategories(animals)
        setStatusData(status)
        setDataSources(sources)
        setRecentAlerts(alerts)
      } catch (error) {
        console.error('Failed to load dashboard:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: '#E4E5ED' }}
      >
        <div className="text-center">
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto"
            style={{ borderColor: '#F05323' }}
          ></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!analytics) return null

  const mortalityRate = (
    (analytics.animalsDeceased / analytics.animalsAffected) *
    100
  ).toFixed(1)

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#E4E5ED' }}>
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* PAGE TITLE */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold" style={{ color: '#2C425A' }}>
            H5N1 Surveillance Dashboard
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Real-time monitoring and surveillance
          </p>
        </div>

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
                trend={`${((analytics.confirmedCases / analytics.totalCases) * 100).toFixed(0)}% of total`}
              />
            </Tooltip>

            <Tooltip content="Number of cases classified as high or critical severity">
              <MetricCard
                title="High/Critical Severity"
                value={(
                  analytics.highSeverity + analytics.criticalSeverity
                ).toLocaleString()}
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Trend Analysis
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* LINE CHART */}
            <Tooltip content="Monthly case trends by animal category">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">
                  Cases Over Time/Animal Category (Could animate this (?))
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  Monthly breakdown by WOAH animal categories
                </p>
                <LineChart data={timelineData} />
              </div>
            </Tooltip>

            {/* PIE CHART - Animal Categories */}
            <Tooltip content="Proportion of cases by WOAH animal categories">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">
                  Animal Category Distribution
                </h3>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Case Status & Data Sources
          </h2>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Regional Breakdown
          </h2>
          <BarChart data={regionData} />
        </section>

        {/*  RECENT ALERTS  */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Alerts
          </h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 divide-y divide-gray-200">
            {recentAlerts.map((alert, index) => (
              <Tooltip key={index} content={alert.message}>
                <div className="p-4 hover:bg-gray-50 transition">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-1 w-2 h-2 rounded-full ${
                          alert.severity === 'high'
                            ? 'bg-red-500'
                            : alert.severity === 'medium'
                              ? 'bg-yellow-500'
                              : 'bg-blue-500'
                        }`}
                      ></div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">
                            {alert.type}
                          </span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-600">
                            {alert.location}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {alert.message}
                        </p>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Severity Summary
          </h2>
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
                  Live data from backend API. Last updated:{' '}
                  {new Date().toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </Tooltip>
      </div>
    </div>
  )
}
