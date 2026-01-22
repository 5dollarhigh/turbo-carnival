import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Receipt APIs
export const uploadScannedReceipt = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/receipts/upload-scan', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadEmailReceipt = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/receipts/upload-email', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getReceipts = async (params = {}) => {
  const response = await api.get('/receipts', { params });
  return response.data;
};

export const getReceipt = async (id) => {
  const response = await api.get(`/receipts/${id}`);
  return response.data;
};

export const deleteReceipt = async (id) => {
  const response = await api.delete(`/receipts/${id}`);
  return response.data;
};

// Analytics APIs
export const getMonthlyTrends = async (months = 12) => {
  const response = await api.get('/analytics/monthly-trends', {
    params: { months },
  });
  return response.data;
};

export const getCategoryBreakdown = async (startDate, endDate) => {
  const response = await api.get('/analytics/category-breakdown', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
};

export const getTopItems = async (limit = 50) => {
  const response = await api.get('/analytics/top-items', {
    params: { limit },
  });
  return response.data;
};

export const getStoreComparison = async () => {
  const response = await api.get('/analytics/store-comparison');
  return response.data;
};

export const getShoppingFrequency = async () => {
  const response = await api.get('/analytics/shopping-frequency');
  return response.data;
};

export const getSummary = async () => {
  const response = await api.get('/analytics/summary');
  return response.data;
};

export const getWasteInsights = async () => {
  const response = await api.get('/analytics/waste-insights');
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/categories');
  return response.data;
};

export default api;
