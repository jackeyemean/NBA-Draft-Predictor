import axios from 'axios';
const BASE = 'http://127.0.0.1:5000/api';

// grabs the default year (2025) from the backend
export const fetchAllResults = () =>
  axios.get(`${BASE}/results`);

export const predict = data =>
  axios.post(`${BASE}/predict`, data);
