import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/.netlify/functions';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('linkcoach_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const setAuthToken = (token) => sessionStorage.setItem('linkcoach_token', token);

export const getDevToken = async () => {
    const response = await fetch('/dev/token');
    if (!response.ok) throw new Error('Failed to get dev token');
    return response.json();
};

export const query = async (question, reportId, conversationHistory = []) => {
    const response = await apiClient.post('/chat', {
        question: question,
        conversationHistory: conversationHistory
    });
    return response.data;
};

export const generateInterpretation = async (data) => {
    const response = await apiClient.post('/generate', data);
    return response.data;
};