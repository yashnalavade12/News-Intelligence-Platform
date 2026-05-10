import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
const api  = axios.create({ baseURL: BASE });

export const getArticles      = (params) => api.get("/api/articles", { params }).then(r => r.data);
export const getStats         = ()        => api.get("/api/articles/stats").then(r => r.data);
export const triggerPipeline  = ()        => api.post("/api/articles/pipeline/run").then(r => r.data);
export const triggerClustering = (n)      => api.post(`/api/articles/pipeline/cluster?n_clusters=${n}`).then(r => r.data);
