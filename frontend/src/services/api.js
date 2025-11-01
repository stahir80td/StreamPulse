/**
 * API Client Service
 * Handles all communication with FastAPI backend
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for logging, auth, etc.)
apiClient.interceptors.request.use(
  (config) => {
    // console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods

/**
 * Get real-time statistics (last 5 minutes)
 */
export const getRealtimeStats = async (minutes = 5) => {
  try {
    const response = await apiClient.get('/stats/realtime', {
      params: { minutes },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching realtime stats:', error);
    throw error;
  }
};

/**
 * Get trending content
 */
export const getTrendingContent = async (minutes = 5, limit = 5) => {
  try {
    const response = await apiClient.get('/stats/trending', {
      params: { minutes, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching trending content:', error);
    throw error;
  }
};

/**
 * Get regional health metrics
 */
export const getRegionalHealth = async (minutes = 5) => {
  try {
    const response = await apiClient.get('/stats/regions', {
      params: { minutes },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching regional health:', error);
    throw error;
  }
};

/**
 * Get alerts
 */
export const getAlerts = async (limit = 10, severity = null, acknowledged = false) => {
  try {
    const response = await apiClient.get('/stats/alerts', {
      params: { limit, severity, acknowledged },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

/**
 * Get time series data
 */
export const getTimeSeries = async (minutes = 60) => {
  try {
    const response = await apiClient.get('/stats/timeseries', {
      params: { minutes },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching time series:', error);
    throw error;
  }
};

/**
 * Get device statistics
 */
export const getDeviceStats = async (minutes = 5, limit = 10) => {
  try {
    const response = await apiClient.get('/stats/devices', {
      params: { minutes, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching device stats:', error);
    throw error;
  }
};

/**
 * Health check
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

/**
 * Fetch all dashboard data in parallel
 */
export const fetchAllDashboardData = async () => {
  try {
    const [stats, trending, regions, alerts, timeseries, devices] = await Promise.all([
      getRealtimeStats(),
      getTrendingContent(),
      getRegionalHealth(),
      getAlerts(),
      getTimeSeries(),
      getDeviceStats(),
    ]);

    return {
      stats,
      trending,
      regions,
      alerts,
      timeseries,
      devices,
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

export default apiClient;