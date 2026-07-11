from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
from app.models.database import db
from app.core.config import settings

router = APIRouter()


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """Get download URL for a document"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "download_url": f"/api/v1/documents/{document_id}/file",
        "filename": doc["filename"],
        "document_id": document_id,
        "title": doc.get("title", doc["filename"])
    }


@router.get("/{document_id}/file")
async def get_document_file(document_id: str):
    """Download the actual document file"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Construct file path
    file_path = Path(settings.UPLOAD_DIR) / doc["filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=doc["filename"],
        media_type='application/octet-stream'
    )


@router.get("/{document_id}/info")
async def get_document_info(document_id: str):
    """Get document information"""
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "title": doc.get("title", doc["filename"]),
        "filename": doc["filename"],
        "file_size": doc.get("file_size", 0),
        "content_type": doc.get("content_type", "application/octet-stream"),
        "upload_timestamp": doc.get("upload_timestamp"),
        "download_url": f"/api/v1/documents/{document_id}/file"
    }
