/**
 * Main Dashboard Component
 * Displays real-time content analytics
 */

import React, { useState, useEffect } from 'react';
import StatsCards from './StatsCards';
import TrendingChart from './TrendingChart';
import RegionChart from './RegionChart';
import TimeSeriesChart from './TimeSeriesChart';
import AlertsList from './AlertsList';
import { fetchAllDashboardData } from '../services/api';
import '../styles/Dashboard.css';

const REFRESH_INTERVAL = parseInt(process.env.REACT_APP_REFRESH_INTERVAL) || 2000;

function Dashboard() {
  const [data, setData] = useState({
    stats: null,
    trending: null,
    regions: null,
    alerts: null,
    timeseries: null,
    devices: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = async () => {
    try {
      const dashboardData = await fetchAllDashboardData();
      setData(dashboardData);
      setLastUpdate(new Date());
      setError(null);
      
      // Only set loading false on first load
      if (loading) {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Retrying...');
      
      // Still set loading false so we can show error
      if (loading) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up polling interval
    const interval = setInterval(fetchData, REFRESH_INTERVAL);

    // Cleanup
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading StreamPulse Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🎬 Stream Pulse</h1>
            <p className="subtitle">Real-Time Content Analytics</p>
          </div>
          <div className="header-info">
            {lastUpdate && (
              <span className="last-update">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            <span className="refresh-indicator">
              <span className="pulse-dot"></span>
              Live
            </span>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <section className="dashboard-section">
        <StatsCards stats={data.stats} />
      </section>

      {/* Alerts */}
      {data.alerts && data.alerts.data && data.alerts.data.length > 0 && (
        <section className="dashboard-section">
          <AlertsList alerts={data.alerts} />
        </section>
      )}

      {/* Trending Content */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2>🔥 Trending Content</h2>
          <span className="section-subtitle">Last 5 minutes</span>
        </div>
        <div className="chart-container">
          {data.trending && data.trending.data && data.trending.data.length > 0 ? (
            <TrendingChart data={data.trending.data} />
          ) : (
            <div className="no-data">No trending data available</div>
          )}
        </div>
      </section>

      {/* Regional Performance */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2>🌍 Regional Performance</h2>
          <span className="section-subtitle">Last 5 minutes</span>
        </div>
        <div className="chart-container">
          {data.regions && data.regions.data && data.regions.data.length > 0 ? (
            <RegionChart data={data.regions.data} />
          ) : (
            <div className="no-data">No regional data available</div>
          )}
        </div>
      </section>

      {/* Time Series */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2>📈 Downloads Over Time</h2>
          <span className="section-subtitle">Last hour</span>
        </div>
        <div className="chart-container">
          {data.timeseries && data.timeseries.data && data.timeseries.data.length > 0 ? (
            <TimeSeriesChart data={data.timeseries.data} />
          ) : (
            <div className="no-data">No time series data available</div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="dashboard-footer">
        <div className="tech-stack">
          <p>
            <strong>Tech Stack:</strong> Kafka (Avro) • Flink • PostgreSQL • FastAPI • React
          </p>
          <p>
            <strong>Deployment:</strong> Upstash • Railway • Neon • Vercel (100% Free Tier)
          </p>
        </div>
        <div className="footer-links">
          <a 
            href="https://github.com/stahir80td/StreamPulse" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <span>•</span>
          <a 
            href={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/docs`}
            target="_blank" 
            rel="noopener noreferrer"
          >
            API Docs
          </a>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard;