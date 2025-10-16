import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Federation
  runDemo: (params: any) => api.post('/demo/run', params),
  
  // Harmonization
  harmonize: (file: FormData) => api.post('/harmonize', file, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  
  // Planning
  generatePlan: (params: any) => api.post('/planner', params),
  
  // Optimization
  optimize: (params: any) => api.post('/optimizer', params),
  
  // Creative
  generateCreative: (params: any) => api.post('/creative', params),
  
  // Policy
  checkPolicy: (params: any) => api.post('/policy', params),
  
  // Clean Room
  queryCleanRoom: (params: any) => api.post('/clean-room/query', params),
  
  // Adapters
  listAdapters: () => api.get('/adapters'),
  getAdapterMetadata: (adapterId: string) => api.get(`/adapters/${adapterId}`),
};
