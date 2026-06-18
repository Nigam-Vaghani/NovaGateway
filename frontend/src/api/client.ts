import axios from "axios";

export const apiClient = axios.create({
  baseURL: "http://localhost:8000/admin",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchRoutes = () => apiClient.get("/routes").then(res => res.data);
export const createRoute = (data: any) => apiClient.post("/routes", data).then(res => res.data);
export const updateRoute = (id: string, data: any) => apiClient.put(`/routes/${id}`, data).then(res => res.data);
export const toggleRoute = (id: string) => apiClient.patch(`/routes/${id}/toggle`).then(res => res.data);
export const deleteRoute = (id: string) => apiClient.delete(`/routes/${id}`).then(res => res.data);

export const fetchBackends = () => apiClient.get("/backends").then(res => res.data);
export const createBackend = (data: any) => apiClient.post("/backends", data).then(res => res.data);
export const updateBackend = (id: string, data: any) => apiClient.put(`/backends/${id}`, data).then(res => res.data);
export const toggleBackend = (id: string) => apiClient.patch(`/backends/${id}/toggle`).then(res => res.data);
export const deleteBackend = (id: string) => apiClient.delete(`/backends/${id}`).then(res => res.data);

export const fetchLogs = (params: any = {}) => apiClient.get("/logs", { params }).then(res => res.data);

export const fetchCacheStats = () => apiClient.get("/cache/stats").then(res => res.data);
export const invalidateCache = (pattern: string) => apiClient.post("/cache/invalidate", { pattern }).then(res => res.data);

export const fetchIpRules = () => apiClient.get("/security/ip-rules").then(res => res.data);
export const createIpRule = (data: any) => apiClient.post("/security/ip-rules", data).then(res => res.data);
export const deleteIpRule = (id: string) => apiClient.delete(`/security/ip-rules/${id}`).then(res => res.data);

export const fetchApiKeys = () => apiClient.get("/security/api-keys").then(res => res.data);
export const createApiKey = (data: any) => apiClient.post("/security/api-keys", data).then(res => res.data);
export const deleteApiKey = (id: string) => apiClient.delete(`/security/api-keys/${id}`).then(res => res.data);

// Dashboard stats:
export const fetchDashboardStats = () => apiClient.get("/logs/dashboard/stats").then(res => res.data);
