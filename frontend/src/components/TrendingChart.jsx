/**
 * Trending Chart Component
 * Bar chart showing top content by downloads
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

function TrendingChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No trending data available</div>;
  }

  // Colors for bars (gradient of blues)
  const COLORS = ['#0071e3', '#1e88e5', '#42a5f5', '#64b5f6', '#90caf9'];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-title">{item.title}</p>
          <p className="tooltip-value">
            <strong>{item.total_downloads.toLocaleString()}</strong> downloads
          </p>
          <p className="tooltip-detail">
            Success Rate: {(item.success_rate * 100).toFixed(1)}%
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
        margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="title"
          angle={-45}
          textAnchor="end"
          height={100}
          tick={{ fill: '#666', fontSize: 12 }}
        />
        <YAxis
          tick={{ fill: '#666', fontSize: 12 }}
          label={{ value: 'Downloads', angle: -90, position: 'insideLeft', fill: '#666' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar
          dataKey="total_downloads"
          fill="#0071e3"
          name="Downloads"
          radius={[8, 8, 0, 0]}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default TrendingChart;