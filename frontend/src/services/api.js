import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5001/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Health check
  healthCheck: () => api.get("/health"),

  // Users
  getAllUsers: () => api.get("/users"),
  getUser: (userId) => api.get(`/users/${userId}`),
  getUserEnrollments: (userId) => api.get(`/users/${userId}/enrollments`),
  getUserStatus: (userId) => api.get(`/users/${userId}/status`),
  getUserSummary: (userId) => api.get(`/users/${userId}/summary`),

  // Courses
  getAllCourses: () => api.get("/courses"),

  // Dashboard
  getDashboard: () => api.get("/dashboard"),

  // Email logs
  getEmailLogs: (page = 1, perPage = 10) =>
    api.get(`/email-logs?page=${page}&per_page=${perPage}`),

  // Stats
  getStats: () => api.get("/stats"),

  // Run job
  runJob: () => api.post("/run-job"),
};

export default apiService;
