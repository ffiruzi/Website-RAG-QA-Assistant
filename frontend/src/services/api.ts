import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Demo credentials - Use environment variables in production
const getDemoCredentials = () => {
  return {
    username: import.meta.env.VITE_DEMO_USERNAME || 'demo@example.com',
    password: import.meta.env.VITE_DEMO_PASSWORD || 'demo123'
  };
};

// Get and cache the token
const getToken = async (): Promise<string> => {
  // Check if token is in localStorage
  let token = localStorage.getItem('token');
  if (token && !isTokenExpired(token)) {
    return token;
  }

  // For demo purposes only - in production, users should login through UI
  try {
    const { username, password } = getDemoCredentials();
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await axios.post(
      '/api/v1/auth/token',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    token = response.data.access_token;
    if (token) {
      localStorage.setItem('token', token);
    }
    return token || '';
  } catch (error) {
    console.error('Failed to get auth token:', error);

    // For development/demo only - create a temporary session
    // In production, redirect to login page
    if (import.meta.env.DEV) {
      console.warn('Using development mode - creating temporary session');
      token = generateTempToken();
      localStorage.setItem('token', token);
      return token;
    }

    // In production, redirect to login
    window.location.href = '/login';
    return '';
  }
};

// Helper function to check if token is expired
const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};

// Generate temporary token for development only
const generateTempToken = (): string => {
  if (!import.meta.env.DEV) {
    throw new Error('Temporary tokens only available in development');
  }

  // Create a basic JWT structure for development
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: 'demo@example.com',
    exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour
  }));
  const signature = 'dev_signature';

  return `${header}.${payload}.${signature}`;
};

// Add request interceptor to include token in headers
api.interceptors.request.use(
  async (config) => {
    // Get token if available
    const token = await getToken();

    // Include token in request headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);

    // If unauthorized or forbidden, try to get a new token and retry
    if (
      (error.response?.status === 401 || error.response?.status === 403) &&
      error.config &&
      !error.config.__isRetry
    ) {
      // Clear the existing token
      localStorage.removeItem('token');

      try {
        // Get a new token and retry
        const token = await getToken();
        error.config.headers.Authorization = `Bearer ${token}`;
        error.config.__isRetry = true;
        return api(error.config);
      } catch (retryError) {
        console.error('Failed to retry with new token:', retryError);

        // In production, redirect to login
        if (!import.meta.env.DEV) {
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;