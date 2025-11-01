/**
 * Region Chart Component
 * Bar chart showing regional performance metrics
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

function RegionChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No regional data available</div>;
  }

  // Get color based on health status
  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#34c759'; // Green
      case 'degraded':
        return '#ff9500'; // Orange
      case 'critical':
        return '#ff3b30'; // Red
      default:
        return '#0071e3'; // Blue
    }
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-title">{item.region}</p>
          <p className="tooltip-value">
            <strong>{item.downloads.toLocaleString()}</strong> downloads
          </p>
          <p className="tooltip-detail">
            Success Rate: {(item.success_rate * 100).toFixed(1)}%
          </p>
          <p className="tooltip-detail">
            Avg Speed: {item.avg_speed.toFixed(1)} Mbps
          </p>
          <p className={`tooltip-status ${item.health_status}`}>
            Status: {item.health_status.toUpperCase()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="region"
          angle={-45}
          textAnchor="end"
          height={80}
          tick={{ fill: '#666', fontSize: 12 }}
        />
        <YAxis
          tick={{ fill: '#666', fontSize: 12 }}
          label={{ value: 'Downloads', angle: -90, position: 'insideLeft', fill: '#666' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar
          dataKey="downloads"
          name="Downloads"
          radius={[8, 8, 0, 0]}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getHealthColor(entry.health_status)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default RegionChart;