/**
 * Stats Cards Component
 * Displays real-time metric cards
 */

import React from 'react';

function StatsCards({ stats }) {
  if (!stats) {
    return (
      <div className="stats-grid">
        <div className="stat-card loading">
          <div className="skeleton"></div>
        </div>
        <div className="stat-card loading">
          <div className="skeleton"></div>
        </div>
        <div className="stat-card loading">
          <div className="skeleton"></div>
        </div>
      </div>
    );
  }

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  const formatPercentage = (num) => {
    return `${(num * 100).toFixed(1)}%`;
  };

  const getSuccessRateColor = (rate) => {
    if (rate >= 0.95) return 'success';
    if (rate >= 0.90) return 'warning';
    return 'critical';
  };

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <h3>Total Downloads</h3>
          <p className="stat-value">{formatNumber(stats.total_downloads)}</p>
          <span className="stat-label">Last 5 minutes</span>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">🎬</div>
        <div className="stat-content">
          <h3>Active Content</h3>
          <p className="stat-value">{formatNumber(stats.unique_content)}</p>
          <span className="stat-label">Unique titles</span>
        </div>
      </div>

      <div className={`stat-card ${getSuccessRateColor(stats.avg_success_rate)}`}>
        <div className="stat-icon">
          {stats.avg_success_rate >= 0.95 ? '✅' : stats.avg_success_rate >= 0.90 ? '⚠️' : '🔴'}
        </div>
        <div className="stat-content">
          <h3>Success Rate</h3>
          <p className="stat-value">{formatPercentage(stats.avg_success_rate)}</p>
          <span className="stat-label">
            {stats.avg_success_rate >= 0.95 
              ? 'Healthy' 
              : stats.avg_success_rate >= 0.90 
              ? 'Degraded' 
              : 'Critical'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default StatsCards;