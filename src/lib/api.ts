import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notebookllm-gruq.onrender.com';

// User role types
export type UserRole = 'student' | 'admin';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export interface DocumentMetadata {
  id: string;
  title: string;
  filename: string;
  file_size: number;
  upload_timestamp: string;
  content_type: string;
  ingestion_status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count?: number;
}

export interface QueryRequest {
  query: string;
  k?: number;
  include_audio?: boolean;
  include_mindmap?: boolean;
}

export interface Citation {
  title: string;
  document_id: string;
  chunk_id: string;
  text_snippet: string;
  confidence_score: number;
  download_url?: string;
  filename?: string;
}

export interface AcademicReasoning {
  reasoning_type: string;
  reasoning: string;
  confidence: number;
  academic_quality: string;
  citations_needed: string[];
  timestamp: string;
}

export interface QueryRequest {
  query: string;
  k?: number;
  include_audio?: boolean;
  include_mindmap?: boolean;
  use_reasoning?: boolean;
  reasoning_type?: string;
}

export interface AcademicQueryRequest {
  query: string;
  k?: number;
  reasoning_type?: string;
  focus_area?: string;
}

export interface LiteratureSummaryRequest {
  focus: string;
  k?: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  mindmap?: MindmapData;
  audio_url?: string;
  processing_time: number;
  reasoning_enabled?: boolean;
  academic_reasoning?: AcademicReasoning;
  enhanced_answer?: string;
  knowledge_base_used?: boolean;
}

export interface AcademicQueryResponse {
  answer: string;
  reasoning_type: string;
  confidence: number;
  academic_quality: string;
  citations_needed: string[];
  citations: Citation[];
  source_documents: Array<{
    content: string;
    metadata: Record<string, any>;
  }>;
  timestamp: string;
  processing_time: number;
  knowledge_base_answer?: string;
  documents_used?: number;
}

export interface LiteratureSummaryResponse {
  summary: string;
  document_count: number;
  focus_area: string;
  academic_quality?: string;
  timestamp?: string;
  citations: Citation[];
  processing_time: number;
}

export interface ReasoningType {
  type: string;
  name: string;
  description: string;
}

export interface MindmapData {
  nodes: Array<{ id: string; label: string; type?: string }>;
  edges: Array<{ from: string; to: string; label?: string }>;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  mindmap?: MindmapData;
  audio_url?: string;
  processing_time: number;
}

export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/v1/auth/login/json', credentials),
  
  register: (userData: { username: string; password: string; email: string; role?: UserRole }) =>
    api.post<{ id: string; username: string; email: string }>('/v1/auth/register', userData),
  
  logout: (sessionId: string) =>
    api.post('/v1/auth/logout', { session_id: sessionId }),
  
  me: () =>
    api.get<User>('/v1/auth/me'),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/v1/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
  
  // Admin: list users
  listUsers: () =>
    api.get<Array<{ id: string; username: string; email: string }>>('/v1/auth/users'),
  
  // Admin: change user role
  changeUserRole: (userId: string, newRole: UserRole) =>
    api.post(`/v1/auth/users/${userId}/change-role`, { new_role: newRole }),
};

export const documentsApi = {
  upload: (file: File, title?: string, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);

    return api.post('/v1/admin/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
  },
  
  list: (page: number = 1, perPage: number = 10) => 
    api.get('/v1/admin/documents', { params: { page, per_page: perPage } }),
  
  getDocument: (documentId: string) =>
    api.get(`/v1/admin/documents/${documentId}`),
  
  deleteDocument: (documentId: string) =>
    api.delete(`/v1/admin/documents/${documentId}`),
  
  triggerIngestion: (documentId: string) =>
    api.post(`/v1/admin/ingest/${documentId}`),
  
  getDocumentStatus: (documentId: string) =>
    api.get(`/v1/admin/documents/${documentId}/status`),
  
  getIngestionJobStatus: (jobId: string) =>
    api.get(`/v1/admin/ingestion-jobs/${jobId}/status`),
  
  // Enhanced download methods
  getDownloadInfo: (documentId: string) =>
    api.get(`/v1/documents/${documentId}/download`),
  
  downloadFile: (documentId: string) =>
    api.get(`/v1/documents/${documentId}/file`, { responseType: 'blob' }),
  
  getDocumentInfo: (documentId: string) =>
    api.get(`/v1/documents/${documentId}/info`),
  
  // Legacy download method (kept for compatibility)
  download: (documentId: string) =>
    api.get(`/v1/documents/${documentId}/file`, { responseType: 'blob' }),
};

export const queryApi = {
  // Standard query with optional reasoning
  submit: (queryRequest: QueryRequest) =>
    api.post<QueryResponse>('/v1/query', queryRequest),
  
  // Academic query with enhanced reasoning
  submitAcademic: (queryRequest: AcademicQueryRequest) =>
    api.post<AcademicQueryResponse>('/v1/query/academic', queryRequest),
  
  // Literature summary generation
  generateSummary: (summaryRequest: LiteratureSummaryRequest) =>
    api.post<LiteratureSummaryResponse>('/v1/query/literature-summary', summaryRequest),
  
  // Get available reasoning types
  getReasoningTypes: () =>
    api.get<{ reasoning_types: ReasoningType[] }>('/v1/query/reasoning-types'),
  
  // Query history
  getHistory: (page: number = 1, perPage: number = 10) =>
    api.get('/v1/query/history', { params: { page, per_page: perPage } }),
  
  // Query details
  getQueryDetails: (queryId: string) =>
    api.get(`/v1/query/${queryId}`),
};

export const adminApi = {
  getStats: () =>
    api.get('/v1/admin/stats'),
  
  getUserRoles: () =>
    api.get('/v1/admin/users/roles'),
  
  changeUserRole: (userId: string, newRole: string) =>
    api.post(`/v1/admin/users/${userId}/change-role`, { new_role: newRole }),
};