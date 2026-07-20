import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
});

api.interceptors.request.use(config => {
  // Buscamos el token de acceso de JWT
  const token = localStorage.getItem('access_token');
  if (token) {
    // JWT usa la palabra Bearer por convención estándar
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default api;