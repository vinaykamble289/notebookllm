import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from typing import Optional
from datetime import datetime
import time

from app.models.schemas import (
    DocumentUploadResponse, DocumentListResponse, DocumentMetadata,
    AdminStats, IngestionStatus, CurrentUser, Role
)
from app.models.database import db
from app.core.config import settings
from app.core.document_processor import document_processor
from app.core.rag_engine import rag_engine
from app.api.v1.auth import require_role

router = APIRouter()


async def process_document_background(doc_id: str, file_path: str):
    """Background task to process document"""
    try:
        # Update status to processing
        db.update_document(doc_id, {"ingestion_status": IngestionStatus.PROCESSING})
        
        # Process document
        documents = document_processor.process_file(file_path)
        
        # Add to vector store
        chunk_count = await rag_engine.add_documents(documents, doc_id)
        
        # Update status to completed
        db.update_document(doc_id, {
            "ingestion_status": IngestionStatus.COMPLETED,
            "chunk_count": chunk_count
        })
        
        print(f"✅ Document {doc_id} processed successfully")
        
    except Exception as e:
        print(f"❌ Error processing document {doc_id}: {e}")
        db.update_document(doc_id, {
            "ingestion_status": IngestionStatus.FAILED,
            "error_message": str(e)
        })


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Upload a document"""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{int(time.time())}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create document record
    doc_id = db.add_document({
        "title": title or file.filename,
        "filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "content_type": file.content_type or "application/octet-stream",
        "ingestion_status": IngestionStatus.PENDING
    })
    
    # Process in background
    background_tasks.add_task(process_document_background, doc_id, file_path)
    
    return {
        "id": doc_id,
        "title": title or file.filename,
        "filename": file.filename,
        "message": "Document uploaded successfully and queued for processing"
    }


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1, 
    per_page: int = 10,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """List all documents"""
    documents, total = db.list_documents(page, per_page)
    
    return {
        "documents": [
            DocumentMetadata(
                id=doc["id"],
                title=doc["title"],
                filename=doc["filename"],
                file_size=doc["file_size"],
                upload_timestamp=datetime.fromisoformat(doc["upload_timestamp"]),
                content_type=doc["content_type"],
                ingestion_status=doc["ingestion_status"],
                chunk_count=doc.get("chunk_count")
            )
            for doc in documents
        ],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Get document details"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Delete a document"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])
    
    # Delete from database
    db.delete_document(document_id)
    
    # Note: FAISS doesn't support deletion easily
    # In production, use a vector DB with delete support
    
    return {"message": "Document deleted successfully"}


@router.post("/ingest/{document_id}")
async def trigger_ingestion(
    document_id: str, 
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Manually trigger document ingestion"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc["ingestion_status"] == IngestionStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="Document is already being processed")
    
    # Process in background
    background_tasks.add_task(process_document_background, document_id, doc["file_path"])
    
    return {"message": "Ingestion triggered", "document_id": document_id}


@router.get("/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Get document processing status"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "status": doc["ingestion_status"],
        "chunk_count": doc.get("chunk_count")
    }


@router.get("/stats", response_model=AdminStats)
async def get_stats(current_user: CurrentUser = Depends(require_role(Role.ADMIN))):
    """Get system statistics"""
    documents, total_docs = db.list_documents(1, 1000)
    queries, total_queries = db.list_queries(1, 1000)
    
    rag_stats = rag_engine.get_stats()
    
    return {
        "total_documents": total_docs,
        "total_chunks": rag_stats["total_vectors"],
        "total_queries": total_queries,
        "vector_store_size": rag_stats["total_vectors"]
    }
