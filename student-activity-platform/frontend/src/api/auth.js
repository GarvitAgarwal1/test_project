import axios from 'axios';

// Avoid circular dependency by using a standard instance for auth calls
const authClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

// For getMe, we need the token, so we can use a small interceptor here or just use the token from localStorage
import api from './axios';

export const authService = {
  login: async (email, password) => {
    // Standard OAuth2 password flow expects form data usually, but let's assume JSON here or adapt as needed.
    // If backend expects x-www-form-urlencoded:
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await authClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  register: async (data) => {
    const response = await authClient.post('/auth/register', data);
    return response.data;
  },

  refreshToken: async () => {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) throw new Error('No refresh token');
    
    const response = await authClient.post('/auth/refresh', { refresh_token });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
