import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import { Icon, LatLngExpression } from 'leaflet';

// Fix default Leaflet icon issues with React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import L from 'leaflet';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// ==================== TYPE DEFINITIONS ====================

interface H5N1Case {
  id: string;
  lat: number;
  lng: number;
  location: string;
  caseType: 'human' | 'avian' | 'dairy' | 'environmental';
  count: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  reportedDate: string;
  status: 'active' | 'contained' | 'monitoring';
  description?: string;
}

interface HotspotZone {
  id: string;
  lat: number;
  lng: number;
  radius: number; // in meters
  caseCount: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

interface MapViewProps {
  cases: H5N1Case[];
  hotspots: HotspotZone[];
  center?: LatLngExpression;
  zoom?: number;
  onCaseClick?: (caseData: H5N1Case) => void;
}

// ==================== HELPER FUNCTIONS ====================

const getCaseIcon = (caseType: H5N1Case['caseType'], severity: H5N1Case['severity']) => {
  const colors: Record<H5N1Case['severity'], string> = {
    low: '#22c55e',
    medium: '#eab308',
    high: '#f97316',
    critical: '#ef4444',
  };

  const shapes: Record<H5N1Case['caseType'], string> = {
    human: '●',
    avian: '▲',
    dairy: '■',
    environmental: '◆',
  };

  return new L.DivIcon({
    className: 'custom-icon',
    html: `
      <div style="
        background-color: ${colors[severity]};
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      ">
        ${shapes[caseType]}
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
};

const getHotspotColor = (riskLevel: HotspotZone['riskLevel']): string => {
  const colors: Record<HotspotZone['riskLevel'], string> = {
    low: '#22c55e',
    medium: '#eab308',
    high: '#f97316',
    critical: '#ef4444',
  };
  return colors[riskLevel];
};

// ==================== MAP CONTROLS COMPONENT ====================

const MapControls: React.FC<{
  showClusters: boolean;
  showHotspots: boolean;
  showHeatmap: boolean;
  filterCaseType: string;
  onToggleClusters: () => void;
  onToggleHotspots: () => void;
  onToggleHeatmap: () => void;
  onFilterChange: (filter: string) => void;
}> = ({
  showClusters,
  showHotspots,
  showHeatmap,
  filterCaseType,
  onToggleClusters,
  onToggleHotspots,
  onToggleHeatmap,
  onFilterChange,
}) => {
  return (
    <div className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-lg p-4 space-y-3">
      <div className="font-semibold text-sm mb-2">Map Controls</div>
      
      {/* Toggle Controls */}
      <label className="flex items-center space-x-2 cursor-pointer">
        <input
          type="checkbox"
          checked={showClusters}
          onChange={onToggleClusters}
          className="w-4 h-4"
        />
        <span className="text-sm">Cluster Markers</span>
      </label>

      <label className="flex items-center space-x-2 cursor-pointer">
        <input
          type="checkbox"
          checked={showHotspots}
          onChange={onToggleHotspots}
          className="w-4 h-4"
        />
        <span className="text-sm">Show Hotspots</span>
      </label>

      <label className="flex items-center space-x-2 cursor-pointer">
        <input
          type="checkbox"
          checked={showHeatmap}
          onChange={onToggleHeatmap}
          className="w-4 h-4"
        />
        <span className="text-sm">Heatmap View</span>
      </label>

      {/* Filter Dropdown */}
      <div className="pt-2 border-t">
        <label className="text-xs font-semibold mb-1 block">Filter by Type</label>
        <select
          value={filterCaseType}
          onChange={(e) => onFilterChange(e.target.value)}
          className="w-full text-sm border rounded px-2 py-1"
        >
          <option value="all">All Cases</option>
          <option value="human">Human Cases</option>
          <option value="avian">Avian Cases</option>
          <option value="dairy">Dairy Cases</option>
          <option value="environmental">Environmental</option>
        </select>
      </div>

      {/* Legend */}
      <div className="pt-2 border-t">
        <div className="text-xs font-semibold mb-1">Case Types</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <span>●</span>
            <span>Human</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>▲</span>
            <span>Avian</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>■</span>
            <span>Dairy</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>◆</span>
            <span>Environmental</span>
          </div>
        </div>
      </div>

      <div className="pt-2 border-t">
        <div className="text-xs font-semibold mb-1">Severity</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Low</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span>Medium</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span>High</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>Critical</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== STATS PANEL COMPONENT ====================

const StatsPanel: React.FC<{ cases: H5N1Case[] }> = ({ cases }) => {
  const humanCases = cases.filter(c => c.caseType === 'human').length;
  const avianCases = cases.filter(c => c.caseType === 'avian').length;
  const dairyCases = cases.filter(c => c.caseType === 'dairy').length;
  const criticalCases = cases.filter(c => c.severity === 'critical').length;

  return (
    <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4">
      <div className="font-semibold text-sm mb-3">Live Statistics</div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-2xl font-bold text-red-600">{humanCases}</div>
          <div className="text-xs text-gray-600">Human Cases</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-600">{avianCases}</div>
          <div className="text-xs text-gray-600">Avian Cases</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-green-600">{dairyCases}</div>
          <div className="text-xs text-gray-600">Dairy Cases</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-orange-600">{criticalCases}</div>
          <div className="text-xs text-gray-600">Critical</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t text-xs text-gray-500">
        Last Updated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

// ==================== MAIN MAP COMPONENT ====================

const BETSMapVisualization: React.FC<MapViewProps> = ({
  cases,
  hotspots,
  center = [39.8283, -98.5795], // Center of USA
  zoom = 5,
  onCaseClick,
}) => {
  const [showClusters, setShowClusters] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [filterCaseType, setFilterCaseType] = useState<string>('all');

  // Filter cases based on selected type
  const filteredCases = cases.filter(
    (c) => filterCaseType === 'all' || c.caseType === filterCaseType
  );

  return (
    <div className="relative w-full h-screen">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Hotspot Zones */}
        {showHotspots &&
          hotspots.map((hotspot) => (
            <Circle
              key={hotspot.id}
              center={[hotspot.lat, hotspot.lng]}
              radius={hotspot.radius}
              pathOptions={{
                fillColor: getHotspotColor(hotspot.riskLevel),
                fillOpacity: 0.2,
                color: getHotspotColor(hotspot.riskLevel),
                weight: 2,
              }}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-bold mb-1">Hotspot Zone</div>
                  <div>Cases: {hotspot.caseCount}</div>
                  <div>Risk Level: {hotspot.riskLevel.toUpperCase()}</div>
                  <div>Radius: {(hotspot.radius / 1000).toFixed(1)} km</div>
                </div>
              </Popup>
            </Circle>
          ))}

        {/* Case Markers with Clustering */}
        {showClusters ? (
          <MarkerClusterGroup
            chunkedLoading
            maxClusterRadius={50}
            spiderfyOnMaxZoom={true}
            showCoverageOnHover={true}
          >
            {filteredCases.map((caseData) => (
              <Marker
                key={caseData.id}
                position={[caseData.lat, caseData.lng]}
                icon={getCaseIcon(caseData.caseType, caseData.severity)}
                eventHandlers={{
                  click: () => onCaseClick?.(caseData),
                }}
              >
                <Popup>
                  <div className="text-sm space-y-1">
                    <div className="font-bold text-base">{caseData.location}</div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">Type:</span>
                      <span className="capitalize">{caseData.caseType}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">Cases:</span>
                      <span>{caseData.count}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">Severity:</span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          caseData.severity === 'critical'
                            ? 'bg-red-100 text-red-800'
                            : caseData.severity === 'high'
                            ? 'bg-orange-100 text-orange-800'
                            : caseData.severity === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {caseData.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">Status:</span>
                      <span className="capitalize">{caseData.status}</span>
                    </div>
                    <div className="text-xs text-gray-600 pt-1">
                      {new Date(caseData.reportedDate).toLocaleDateString()}
                    </div>
                    {caseData.description && (
                      <div className="pt-2 border-t text-xs">{caseData.description}</div>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}
          </MarkerClusterGroup>
        ) : (
          // Non-clustered markers
          filteredCases.map((caseData) => (
            <Marker
              key={caseData.id}
              position={[caseData.lat, caseData.lng]}
              icon={getCaseIcon(caseData.caseType, caseData.severity)}
              eventHandlers={{
                click: () => onCaseClick?.(caseData),
              }}
            >
              <Popup>
                <div className="text-sm space-y-1">
                  <div className="font-bold text-base">{caseData.location}</div>
                  <div>Type: {caseData.caseType}</div>
                  <div>Cases: {caseData.count}</div>
                  <div>Severity: {caseData.severity}</div>
                  <div>Status: {caseData.status}</div>
                  <div className="text-xs text-gray-600">
                    {new Date(caseData.reportedDate).toLocaleDateString()}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))
        )}
      </MapContainer>

      {/* Map Controls */}
      <MapControls
        showClusters={showClusters}
        showHotspots={showHotspots}
        showHeatmap={showHeatmap}
        filterCaseType={filterCaseType}
        onToggleClusters={() => setShowClusters(!showClusters)}
        onToggleHotspots={() => setShowHotspots(!showHotspots)}
        onToggleHeatmap={() => setShowHeatmap(!showHeatmap)}
        onFilterChange={setFilterCaseType}
      />

      {/* Stats Panel */}
      <StatsPanel cases={filteredCases} />
    </div>
  );
};

export default BETSMapVisualization;
export type { H5N1Case, HotspotZone };
