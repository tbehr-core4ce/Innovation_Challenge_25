/**
 * BETS Dashboard - Complete Integration Example
 * Shows how to connect the map visualization with the FastAPI backend
 */

import React, { useState, useEffect } from 'react';
import BETSMapVisualization, { H5N1Case, HotspotZone } from './BETSMapVisualization';
import { betsApi } from './betsApiService';

const BETSDashboard: React.FC = () => {
  // State management
  const [cases, setCases] = useState<H5N1Case[]>([]);
  const [hotspots, setHotspots] = useState<HotspotZone[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [refreshInterval, setRefreshInterval] = useState<number>(30000); // 30 seconds

  // Fetch data from API
  const fetchMapData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await betsApi.getMapData();
      setCases(data.cases);
      setHotspots(data.hotspots);
      setLastUpdated(new Date(data.lastUpdated).toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      console.error('Error fetching map data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchMapData();
  }, []);

  // Auto-refresh data
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchMapData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  // Handle case click
  const handleCaseClick = (caseData: H5N1Case) => {
    console.log('Case clicked:', caseData);
    // You could open a modal, side panel, or update a details view
    alert(`${caseData.location}\n${caseData.count} ${caseData.caseType} case(s)\nSeverity: ${caseData.severity}`);
  };

  // Loading state
  if (loading && cases.length === 0) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-700">Loading BETS data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-gray-100">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <div className="text-red-600 text-xl font-bold mb-4">Error Loading Data</div>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={fetchMapData}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
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
            <span className="text-sm text-gray-500">H5N1 Surveillance Dashboard</span>
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

      {/* Map Visualization */}
      <div className="pt-16 w-full h-full">
        <BETSMapVisualization
          cases={cases}
          hotspots={hotspots}
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
  );
};

export default BETSDashboard;
