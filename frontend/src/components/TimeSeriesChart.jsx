/**
 * Time Series Chart Component
 * Line chart showing downloads over time
 * Mobile-responsive
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function TimeSeriesChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No time series data available</div>;
  }

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-title">
            {new Date(item.window_start).toLocaleString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
            })}
          </p>
          <p className="tooltip-value">
            <strong>{item.total_downloads.toLocaleString()}</strong> downloads
          </p>
          {item.success_rate && (
            <p className="tooltip-detail">
              Success Rate: {(item.success_rate * 100).toFixed(1)}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Responsive tick count based on screen width
  const getTickCount = () => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < 768 ? 4 : 8;
    }
    return 8;
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={data}
        margin={{ 
          top: 20, 
          right: window.innerWidth < 768 ? 10 : 30, 
          left: window.innerWidth < 768 ? 0 : 20, 
          bottom: 20 
        }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="window_start"
          tickFormatter={formatTime}
          tick={{ fill: '#666', fontSize: window.innerWidth < 768 ? 10 : 12 }}
          angle={window.innerWidth < 768 ? -45 : 0}
          textAnchor={window.innerWidth < 768 ? 'end' : 'middle'}
          height={window.innerWidth < 768 ? 60 : 30}
          interval="preserveStartEnd"
          tickCount={getTickCount()}
        />
        <YAxis
          tick={{ fill: '#666', fontSize: window.innerWidth < 768 ? 10 : 12 }}
          label={
            window.innerWidth >= 768
              ? { value: 'Downloads', angle: -90, position: 'insideLeft', fill: '#666' }
              : undefined
          }
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          wrapperStyle={{ fontSize: window.innerWidth < 768 ? 12 : 14 }}
        />
        <Line
          type="monotone"
          dataKey="total_downloads"
          stroke="#0071e3"
          strokeWidth={2}
          name="Downloads"
          dot={{ r: window.innerWidth < 768 ? 2 : 4 }}
          activeDot={{ r: window.innerWidth < 768 ? 4 : 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default TimeSeriesChart;