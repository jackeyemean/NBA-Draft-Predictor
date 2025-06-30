// src/api.js
import axios from 'axios';
const BASE = 'http://127.0.0.1:5000/api';

export const fetchAllResults = () =>
  axios.get(`${BASE}/results`);

export const predict = data =>
  axios.post(`${BASE}/predict`, data);
