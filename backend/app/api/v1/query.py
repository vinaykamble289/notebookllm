from fastapi import APIRouter, HTTPException
import time
from typing import List

from app.models.schemas import (
    QueryRequest, QueryResponse, Citation,
    QueryHistoryResponse, QueryHistoryItem,
    AcademicQueryRequest, AcademicQueryResponse,
    LiteratureSummaryRequest, LiteratureSummaryResponse,
    AcademicReasoning
)
from app.models.database import db
from app.core.rag_engine import rag_engine

router = APIRouter()


def extract_citations(source_documents) -> List[Citation]:
    """Extract citations from source documents with download links"""
    citations = []
    
    for i, doc in enumerate(source_documents):
        metadata = doc.metadata
        document_id = metadata.get("document_id", "unknown")
        
        # Get document info from database for download link
        try:
            doc_info = db.get_document(document_id)
            filename = doc_info.get("filename", "Unknown") if doc_info else "Unknown"
            download_url = f"/api/v1/documents/{document_id}/download" if document_id != "unknown" else None
        except:
            filename = metadata.get("source", "Unknown")
            download_url = None
        
        citations.append(Citation(
            title=metadata.get("source", "Unknown"),
            document_id=document_id,
            chunk_id=metadata.get("chunk_id", f"chunk_{i}"),
            text_snippet=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            confidence_score=0.85,  # Placeholder - FAISS doesn't provide scores directly
            download_url=download_url,
            filename=filename
        ))
    
    return citations


@router.post("", response_model=QueryResponse)
async def submit_query(query_request: QueryRequest):
    """Submit a query to the RAG system with optional reasoning"""
    start_time = time.time()
    
    try:
        # Query RAG engine with reasoning
        result = await rag_engine.query(
            query_request.query,
            k=query_request.k,
            use_reasoning=query_request.use_reasoning
        )
        
        # Extract citations
        citations = extract_citations(result["source_documents"])
        
        # Prepare academic reasoning if available
        academic_reasoning = None
        if result.get("academic_reasoning"):
            reasoning_data = result["academic_reasoning"]
            academic_reasoning = AcademicReasoning(
                reasoning_type=reasoning_data.get("reasoning_type", "unknown"),
                reasoning=reasoning_data.get("reasoning", ""),
                confidence=reasoning_data.get("confidence", 0.0),
                academic_quality=reasoning_data.get("academic_quality", "unknown"),
                citations_needed=reasoning_data.get("citations_needed", []),
                timestamp=reasoning_data.get("timestamp", "")
            )
        
        # Save query to database
        db.add_query({
            "user_id": query_request.user_id or "anonymous",
            "query_text": query_request.query,
            "answer": result.get("enhanced_answer", result["answer"]),
            "reasoning_enabled": result.get("reasoning_enabled", False)
        })
        
        processing_time = time.time() - start_time
        
        response = QueryResponse(
            answer=result["answer"],
            citations=citations,
            processing_time=processing_time,
            reasoning_enabled=result.get("reasoning_enabled", False),
            academic_reasoning=academic_reasoning,
            enhanced_answer=result.get("enhanced_answer")
        )
        
        # Optional: Generate mindmap (simplified)
        if query_request.include_mindmap:
            response.mindmap = {
                "nodes": [
                    {"id": "1", "label": "Query", "type": "question"},
                    {"id": "2", "label": "Answer", "type": "answer"},
                ],
                "edges": [
                    {"from": "1", "to": "2", "label": "generates"}
                ]
            }
        
        # Optional: Generate audio (placeholder)
        if query_request.include_audio:
            response.audio_url = None  # TTS not implemented
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/academic", response_model=AcademicQueryResponse)
async def submit_academic_query(query_request: AcademicQueryRequest):
    """Submit an academic query with enhanced reasoning capabilities"""
    start_time = time.time()
    
    try:
        # Use academic query method
        result = await rag_engine.academic_query(
            query_request.query,
            k=query_request.k,
            reasoning_type=query_request.reasoning_type
        )
        
        processing_time = time.time() - start_time
        
        # Extract citations from source documents
        citations = extract_citations(result.get("source_documents", []))
        
        # Convert source documents to serializable format
        source_docs = []
        for doc in result.get("source_documents", []):
            source_docs.append({
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "metadata": doc.metadata
            })
        
        response = AcademicQueryResponse(
            answer=result["answer"],
            reasoning_type=result.get("reasoning_type", "unknown"),
            confidence=result.get("confidence", 0.0),
            academic_quality=result.get("academic_quality", "unknown"),
            citations_needed=result.get("citations_needed", []),
            citations=citations,  # Add citations with download links
            source_documents=source_docs,
            timestamp=result.get("timestamp", ""),
            processing_time=processing_time,
            knowledge_base_answer=result.get("knowledge_base_answer"),
            documents_used=result.get("documents_used", 0)
        )
        
        # Save academic query to database
        db.add_query({
            "user_id": query_request.user_id or "anonymous",
            "query_text": query_request.query,
            "answer": result["answer"],
            "query_type": "academic",
            "reasoning_type": result.get("reasoning_type"),
            "confidence": result.get("confidence"),
            "academic_quality": result.get("academic_quality")
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Academic query processing failed: {str(e)}"
        )


@router.post("/literature-summary", response_model=LiteratureSummaryResponse)
async def generate_literature_summary(request: LiteratureSummaryRequest):
    """Generate an academic literature summary from the document collection"""
    start_time = time.time()
    
    try:
        result = await rag_engine.generate_literature_summary(
            focus=request.focus,
            k=request.k
        )
        
        processing_time = time.time() - start_time
        
        # Extract citations from documents used in summary
        source_docs = result.get("source_documents", [])
        citations = extract_citations(source_docs) if source_docs else []
        
        response = LiteratureSummaryResponse(
            summary=result.get("summary", ""),
            document_count=result.get("document_count", 0),
            focus_area=result.get("focus_area", request.focus),
            academic_quality=result.get("academic_quality"),
            timestamp=result.get("timestamp"),
            citations=citations,  # Add citations
            processing_time=processing_time
        )
        
        # Save summary generation to database
        db.add_query({
            "user_id": request.user_id or "anonymous",
            "query_text": f"Literature summary: {request.focus}",
            "answer": result.get("summary", ""),
            "query_type": "literature_summary",
            "focus_area": request.focus,
            "document_count": result.get("document_count", 0)
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Literature summary generation failed: {str(e)}"
        )


@router.get("/reasoning-types")
async def get_reasoning_types():
    """Get available reasoning types for academic queries"""
    return {
        "reasoning_types": [
            {
                "type": "research_analysis",
                "name": "Research Analysis",
                "description": "Comprehensive analysis of research problems and findings"
            },
            {
                "type": "methodology_review",
                "name": "Methodology Review",
                "description": "Detailed evaluation of research methodologies and approaches"
            },
            {
                "type": "literature_synthesis",
                "name": "Literature Synthesis",
                "description": "Systematic synthesis of academic literature and sources"
            },
            {
                "type": "critical_evaluation",
                "name": "Critical Evaluation",
                "description": "Critical assessment of academic work and evidence"
            },
            {
                "type": "concept_explanation",
                "name": "Concept Explanation",
                "description": "Clear explanation of complex academic concepts"
            },
            {
                "type": "research_proposal",
                "name": "Research Proposal",
                "description": "Framework for developing research proposals"
            }
        ]
    }


@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(page: int = 1, per_page: int = 10):
    """Get query history"""
    queries, total = db.list_queries(page, per_page)
    
    return {
        "queries": [
            QueryHistoryItem(
                id=q["id"],
                query=q["query"],
                answer=q["answer"],
                timestamp=q["timestamp"]
            )
            for q in queries
        ],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{query_id}")
async def get_query_details(query_id: str):
    """Get details of a specific query"""
    query = db.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query
