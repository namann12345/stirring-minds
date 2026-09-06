// frontend/src/api/client.js
// Axios API client for communicating with backend
import axios from 'axios';

// Get API URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('🔗 Connecting to API:', API_BASE_URL); // Debug log

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
  withCredentials: true, // Important for CORS with credentials
});


// Request interceptor - Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Success:', response.config.url); // Debug log
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.config?.url); // Debug log

    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      console.log('🔐 Unauthorized - Redirecting to login');
      clearAuthToken();
      window.location.href = '/';
    } else if (error.response?.status === 403) {
      console.error('🚫 Forbidden: Insufficient permissions');
    } else if (error.response?.status === 500) {
      console.error('🔥 Server error:', error.response.data);
    } else if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      console.error('🔌 Connection Error: Backend not reachable at', API_BASE_URL);
      alert('Cannot connect to server. Please ensure backend is running on ' + API_BASE_URL);
    }

    return Promise.reject(error);
  }
);

// Export default client
export default apiClient;

// ============================================================================
// API FUNCTIONS - Organized by feature
// ============================================================================

// Authentication APIs
export const authAPI = {
  login: (credentials) => apiClient.post('/api/auth/login', credentials),
  register: (userData) => apiClient.post('/api/auth/register', userData),
  getMe: () => apiClient.get('/api/auth/me'),
  logout: () => {
    clearAuthToken();
    window.location.href = '/';
  }
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => apiClient.get('/api/dashboard/stats'),
  getKPIs: (department) => apiClient.get(`/api/dashboard/kpis/${department}`),
  getActivity: (limit = 10) => apiClient.get(`/api/dashboard/activity?limit=${limit}`),
};

// Reports APIs
export const reportsAPI = {
  generate: (reportData) => apiClient.post('/api/reports/generate', reportData),
  getAll: (params) => apiClient.get('/api/reports', { params }),
  getById: (id) => apiClient.get(`/api/reports/${id}`),
  download: (id) => apiClient.get(`/api/reports/${id}/download`),
  delete: (id) => apiClient.delete(`/api/reports/${id}`),
};

// Query APIs (AI Assistant)
export const queryAPI = {
  process: (queryData) => apiClient.post('/api/query', queryData),
  processVoice: (formData) => {
    return apiClient.post('/api/query/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

// Alerts APIs
export const alertsAPI = {
  getAll: (params) => apiClient.get('/api/alerts', { params }),
  acknowledge: (id) => apiClient.post(`/api/alerts/${id}/acknowledge`),
  create: (alertData) => apiClient.post('/api/alerts/create', alertData),
};

// Comments APIs (Collaboration)
export const commentsAPI = {
  create: (commentData) => apiClient.post('/api/comments', commentData),
  getByReport: (reportId) => apiClient.get(`/api/comments/${reportId}`),
  reply: (commentId, replyData) => apiClient.post(`/api/comments/${commentId}/reply`, replyData),
  delete: (commentId) => apiClient.delete(`/api/comments/${commentId}`),
};

// Settings APIs
export const settingsAPI = {
  get: () => apiClient.get('/api/settings'),
  update: (settings) => apiClient.put('/api/settings', settings),
  setupIntegration: (service, data) =>
    apiClient.post(`/api/settings/integrations/${service}`, data),
};

// Analytics APIs
export const analyticsAPI = {
  forecast: (forecastData) => apiClient.post('/api/analytics/forecast', forecastData),
  detectAnomalies: (department) => apiClient.get(`/api/analytics/anomalies/${department}`),
  getRecommendations: (requestData) => apiClient.post('/api/analytics/recommendations', requestData),
};

// Data Upload APIs
export const dataAPI = {
  upload: (formData) => {
    return apiClient.post('/api/data/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getSources: () => apiClient.get('/api/data/sources'),
};

// Scheduling APIs
export const scheduleAPI = {
  createSchedule: (scheduleData) => apiClient.post('/api/schedule/report', scheduleData),
  getSchedules: () => apiClient.get('/api/schedule/list'),
  cancelSchedule: (scheduleId) => apiClient.delete(`/api/schedule/${scheduleId}`),
};

// Admin APIs (Admin only)
export const adminAPI = {
  getAllUsers: () => apiClient.get('/api/admin/users'),
  updateUserRole: (userId, roleData) => apiClient.put(`/api/admin/users/${userId}/role`, roleData),
  deleteUser: (userId) => apiClient.delete(`/api/admin/users/${userId}`),
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

// Clear all auth tokens
export const clearAuthToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token');
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
};

// Store auth token
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('access_token', token);
    localStorage.setItem('token', token);
    localStorage.setItem('auth_token', token);
  }
};

// Get auth token
export const getAuthToken = () => {
  return localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('auth_token');
};

// Store user data
export const setUserData = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

// Get user data
export const getUserData = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getAuthToken();
};

// Handle API errors
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
    return {
      error: true,
      message,
      status: error.response.status
    };
  } else if (error.request) {
    // Request made but no response
    return {
      error: true,
      message: 'No response from server. Please check your connection.',
      status: 0
    };
  } else {
    // Error in request setup
    return {
      error: true,
      message: error.message || 'An unexpected error occurred',
      status: -1
    };
  }
};

// Format API response
export const formatResponse = (response) => {
  return {
    success: true,
    data: response.data,
    status: response.status
  };
};