from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Auth Schemas
class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[Role] = Role.STUDENT


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    username: str
    role: Role = Role.STUDENT


class ChangeRoleRequest(BaseModel):
    new_role: Role


class CurrentUser(BaseModel):
    id: str
    username: str
    email: str
    role: Role = Role.STUDENT


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: Role = Role.STUDENT


# Document Schemas
class DocumentMetadata(BaseModel):
    id: str
    title: str
    filename: str
    file_size: int
    upload_timestamp: datetime
    content_type: str
    ingestion_status: IngestionStatus
    chunk_count: Optional[int] = None


class DocumentUploadResponse(BaseModel):
    id: str
    title: str
    filename: str
    message: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int
    page: int
    per_page: int


# Query Schemas
class Citation(BaseModel):
    title: str
    document_id: str
    chunk_id: str
    text_snippet: str
    confidence_score: float
    download_url: Optional[str] = None
    filename: Optional[str] = None


class AcademicReasoning(BaseModel):
    reasoning_type: str
    reasoning: str
    confidence: float
    academic_quality: str
    citations_needed: List[str]
    timestamp: str


class MindmapNode(BaseModel):
    id: str
    label: str
    type: Optional[str] = None


class MindmapEdge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    label: Optional[str] = None


class MindmapData(BaseModel):
    nodes: List[MindmapNode]
    edges: List[MindmapEdge]


class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None  # Optional - can be provided for authenticated users
    k: int = 8
    include_audio: bool = False
    include_mindmap: bool = False
    use_reasoning: bool = True
    reasoning_type: Optional[str] = "auto"  # auto, research_analysis, methodology_review, etc.


class AcademicQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None  # Optional - can be provided for authenticated users
    k: int = 8
    reasoning_type: str = "auto"
    focus_area: Optional[str] = "general"


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    mindmap: Optional[MindmapData] = None
    audio_url: Optional[str] = None
    processing_time: float
    reasoning_enabled: Optional[bool] = False
    academic_reasoning: Optional[AcademicReasoning] = None
    enhanced_answer: Optional[str] = None
    knowledge_base_used: Optional[bool] = False


class AcademicQueryResponse(BaseModel):
    answer: str
    reasoning_type: str
    confidence: float
    academic_quality: str
    citations_needed: List[str]
    citations: List[Citation]  # Add citations with download links
    source_documents: List[Dict[str, Any]]
    timestamp: str
    processing_time: float
    knowledge_base_answer: Optional[str] = None
    documents_used: Optional[int] = None


class LiteratureSummaryRequest(BaseModel):
    focus: str = "general"
    user_id: Optional[str] = None  # Optional - can be provided for authenticated users
    k: int = 15


class LiteratureSummaryResponse(BaseModel):
    summary: str
    document_count: int
    focus_area: str
    academic_quality: Optional[str] = None
    timestamp: Optional[str] = None
    citations: List[Citation] = []
    processing_time: float


class QueryHistoryItem(BaseModel):
    id: str
    query: str
    answer: str
    timestamp: datetime


class QueryHistoryResponse(BaseModel):
    queries: List[QueryHistoryItem]
    total: int
    page: int
    per_page: int


# Admin Schemas
class AdminStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    vector_store_size: int


class IngestionJobStatus(BaseModel):
    job_id: str
    document_id: str
    status: IngestionStatus
    progress: float
    message: Optional[str] = None
