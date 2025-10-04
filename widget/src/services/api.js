import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
    const response = await apiClient.post('/api/v1/coaching/query-non-streaming', {
        user_id: 'dev_user_123',
        report_id: reportId,
        question: question,
        conversation_history: conversationHistory
    });
    return response.data;
};

export const generateInterpretation = async (data) => {
    const response = await apiClient.post('/api/v1/coaching/interpretation', data);
    return response.data;
};