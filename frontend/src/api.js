import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const client = axios.create({ baseURL: API_BASE, timeout: 15000 });

export const getDashboard = () => client.get("/api/dashboard").then((r) => r.data);

export const analyzeNews = (text) =>
  client.post("/api/analyze-news", { text }).then((r) => r.data);
