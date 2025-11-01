/**
 * Alerts List Component
 * Displays recent alerts with severity indicators
 * Mobile-responsive
 */

import React from 'react';

function AlertsList({ alerts }) {
  if (!alerts || !alerts.data || alerts.data.length === 0) {
    return null; // Don't show section if no alerts
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return '🔴';
      case 'WARNING':
        return '⚠️';
      case 'INFO':
        return 'ℹ️';
      default:
        return '📌';
    }
  };

  const getSeverityClass = (severity) => {
    return severity.toLowerCase();
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="alerts-section">
      <div className="section-header">
        <h2>⚠️ Alerts</h2>
        {alerts.unacknowledged_count > 0 && (
          <span className="alert-badge">{alerts.unacknowledged_count}</span>
        )}
      </div>
      <div className="alerts-list">
        {alerts.data.map((alert) => (
          <div
            key={alert.id}
            className={`alert-item ${getSeverityClass(alert.severity)}`}
          >
            <div className="alert-icon">
              {getSeverityIcon(alert.severity)}
            </div>
            <div className="alert-content">
              <div className="alert-header">
                <span className="alert-type">{alert.alert_type.replace(/_/g, ' ')}</span>
                <span className="alert-time">{formatTime(alert.created_at)}</span>
              </div>
              <p className="alert-message">{alert.message}</p>
              {alert.region && (
                <div className="alert-meta">
                  <span className="alert-region">📍 {alert.region}</span>
                  {alert.metric_value && alert.threshold_value && (
                    <span className="alert-metric">
                      {alert.metric_name}: {alert.metric_value.toFixed(2)} 
                      (threshold: {alert.threshold_value.toFixed(2)})
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AlertsList;