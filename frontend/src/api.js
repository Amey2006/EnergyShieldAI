// import axios from "axios";

// const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// export const client = axios.create({ baseURL: API_BASE, timeout: 15000 });

// export const getDashboard = () => client.get("/api/dashboard").then((r) => r.data);

// export const analyzeNews = (text) =>
//   client.post("/api/analyze-news", { text }).then((r) => r.data);


import axios from "axios";

// Clean base URL to prevent double slashes like '...com//api/dashboard'
const rawBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const API_BASE = rawBase.replace(/\/+$/, "");

export const client = axios.create({ 
  baseURL: API_BASE, 
  timeout: 15000 
});

// Response Interceptor for better debugging in Console
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ERR_NETWORK") {
      console.error(
        `[API Error] Could not connect to backend at ${API_BASE}. Check CORS or VITE_API_BASE env var.`
      );
    }
    return Promise.reject(error);
  }
);

export const getDashboard = () => client.get("/api/dashboard").then((r) => r.data);

export const analyzeNews = (text) =>
  client.post("/api/analyze-news", { text }).then((r) => r.data);