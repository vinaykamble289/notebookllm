import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from langchain.schema import Document
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from app.core.config import settings
from app.core.reasoning_engine import reasoning_engine


class RAGEngine:
    """Enhanced RAG Engine with FAISS vector store and academic reasoning capabilities"""
    
    def __init__(self):
        self.embedding_model = None
        self.vectorstore = None
        self.llm = None
        self.text_splitter = None
        self.retriever = None
        self.qa_chain = None
        self.reasoning_enabled = True
        self.index_path = Path(settings.VECTOR_STORE_DIR) / settings.FAISS_INDEX_NAME
        self.metadata_path = Path(settings.VECTOR_STORE_DIR) / "metadata.pkl"
        
    async def initialize(self):
        """Initialize the RAG engine and load existing vector store"""
        print("🔧 Initializing embedding model...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        print("🔧 Initializing text splitter...")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Load or create vector store
        if self.index_path.exists():
            print("📂 Loading existing vector store...")
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.index_path),
                    self.embedding_model
                )
                print(f"✅ Loaded vector store with {self.vectorstore.index.ntotal} vectors")
            except Exception as e:
                print(f"⚠️ Could not load existing vector store: {e}")
                print("🆕 Creating new vector store...")
                self.vectorstore = FAISS.from_texts(
                    ["Initialization document"],
                    self.embedding_model,
                    metadatas=[{"source": "init", "document_id": "init"}]
                )
                self._save_vectorstore()
        else:
            print("🆕 Creating new vector store...")
            # Create empty vector store
            self.vectorstore = FAISS.from_texts(
                ["Initialization document"],
                self.embedding_model,
                metadatas=[{"source": "init", "document_id": "init"}]
            )
            self._save_vectorstore()
        
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 8}
        )
        
        print("🔧 Initializing LLM...")
        self._initialize_llm()
        
        print("🔧 Creating QA chain...")
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )
        
        # Initialize reasoning engine
        if self.reasoning_enabled:
            print("🧠 Initializing academic reasoning engine...")
            try:
                await reasoning_engine.initialize()
                print("✅ Academic reasoning engine ready")
            except Exception as e:
                print(f"⚠️ Could not initialize reasoning engine: {e}")
                self.reasoning_enabled = False
        
    def _initialize_llm(self):
        """Initialize the language model"""
        tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(settings.LLM_MODEL)
        
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=settings.MAX_TOKENS
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)
    
    def _save_vectorstore(self):
        """Save vector store to disk"""
        self.vectorstore.save_local(str(self.index_path))
        print(f"💾 Vector store saved to {self.index_path}")
    
    async def add_documents(self, documents: List[Document], document_id: str) -> int:
        """Add documents to the vector store"""
        # Validate documents
        if not documents:
            raise ValueError("No documents provided. The file may be empty or unreadable.")
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Validate chunks
        if not chunks:
            raise ValueError("No text chunks generated. The document may be empty or contain only images.")
        
        # Add metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "document_id": document_id,
                "chunk_id": f"{document_id}_chunk_{i}",
                "chunk_index": i
            })
        
        # Add to vector store
        if self.vectorstore.index.ntotal == 1:
            # Remove init document if this is the first real document
            self.vectorstore = FAISS.from_documents(chunks, self.embedding_model)
        else:
            self.vectorstore.add_documents(chunks)
        
        # Save to disk
        self._save_vectorstore()
        
        # Update retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 8})
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )
        
        return len(chunks)
    
    async def query(self, question: str, k: int = 8, use_reasoning: bool = True) -> Dict[str, Any]:
        """Enhanced query with academic reasoning capabilities based on knowledge base"""
        if not self.qa_chain:
            raise RuntimeError("RAG engine not initialized")
        
        # Update retriever k value
        self.retriever.search_kwargs["k"] = k
        
        # Get relevant documents from knowledge base first
        relevant_docs = self.retriever.get_relevant_documents(question)
        
        # Run basic RAG query to get knowledge base answer
        result = self.qa_chain.invoke({"query": question})
        base_answer = result["result"]
        source_documents = result.get("source_documents", relevant_docs)
        
        response = {
            "answer": base_answer,
            "source_documents": source_documents,
            "reasoning_enabled": self.reasoning_enabled and use_reasoning,
            "knowledge_base_used": len(source_documents) > 0
        }
        
        # Add academic reasoning if enabled and we have documents
        if self.reasoning_enabled and use_reasoning and source_documents:
            try:
                # Enhanced question that emphasizes using the knowledge base
                enhanced_question = f"""
Based on the documents in the knowledge base, {question}

IMPORTANT: Use ONLY the information from the provided documents. The knowledge base context shows: {base_answer}
"""
                
                reasoning_result = await reasoning_engine.reason(enhanced_question, source_documents)
                
                # Ensure reasoning is grounded in knowledge base
                reasoning_text = reasoning_result.get("reasoning", "")
                if reasoning_text:
                    reasoning_text = f"""**Analysis based on your knowledge base:**

{reasoning_text}

**Original knowledge base answer:** {base_answer}"""
                
                response.update({
                    "academic_reasoning": reasoning_result,
                    "enhanced_answer": self._combine_rag_and_reasoning(
                        base_answer, 
                        reasoning_text
                    )
                })
            except Exception as e:
                print(f"⚠️ Reasoning engine error: {e}")
                response["reasoning_error"] = str(e)
        
        return response
    
    async def academic_query(self, question: str, k: int = 8, reasoning_type: str = "auto") -> Dict[str, Any]:
        """Specialized academic query with enhanced reasoning based on knowledge base"""
        if not self.qa_chain:
            raise RuntimeError("RAG engine not initialized")
        
        # Get relevant documents from knowledge base
        self.retriever.search_kwargs["k"] = k
        relevant_docs = self.retriever.get_relevant_documents(question)
        
        if not relevant_docs:
            return {
                "answer": "No relevant documents found in your knowledge base for this query. Please upload relevant academic documents first.",
                "reasoning_type": "no_documents",
                "confidence": 0.0,
                "academic_quality": "low",
                "citations_needed": [],
                "source_documents": [],
                "timestamp": "",
                "error": "No documents in knowledge base"
            }
        
        # First get basic RAG answer to ensure we're using the knowledge base
        try:
            rag_result = self.qa_chain.invoke({"query": question})
            base_answer = rag_result["result"]
            source_documents = rag_result.get("source_documents", relevant_docs)
        except Exception as e:
            print(f"⚠️ RAG query error: {e}")
            base_answer = "Error retrieving information from knowledge base."
            source_documents = relevant_docs
        
        # Use reasoning engine for academic analysis ONLY if we have documents
        if self.reasoning_enabled and source_documents:
            try:
                # Enhanced prompt that emphasizes using ONLY the provided documents
                enhanced_question = f"""
Based STRICTLY on the provided documents from the knowledge base, {question}

IMPORTANT: You must base your analysis ONLY on the information contained in the provided documents. Do not use external knowledge or general information not present in these documents. If the documents don't contain sufficient information to answer the question, clearly state this limitation.

Knowledge Base Context: {base_answer}
"""
                
                reasoning_result = await reasoning_engine.reason(enhanced_question, source_documents)
                
                # Ensure the reasoning is grounded in the knowledge base
                reasoning_text = reasoning_result.get("reasoning", "")
                
                # Add a disclaimer if the reasoning seems to go beyond the documents
                if reasoning_text and len(reasoning_text) > 100:
                    reasoning_text = f"""**Based on the provided documents in your knowledge base:**

{reasoning_text}

**Note:** This analysis is based solely on the documents in your knowledge base. For more comprehensive analysis, consider uploading additional relevant academic sources."""
                
                return {
                    "answer": reasoning_text if reasoning_text else base_answer,
                    "reasoning_type": reasoning_result.get("reasoning_type", "research_analysis"),
                    "confidence": reasoning_result.get("confidence", 0.0),
                    "academic_quality": reasoning_result.get("academic_quality", "unknown"),
                    "citations_needed": reasoning_result.get("citations_needed", []),
                    "source_documents": source_documents,
                    "timestamp": reasoning_result.get("timestamp", ""),
                    "knowledge_base_answer": base_answer,  # Include the original RAG answer
                    "documents_used": len(source_documents)
                }
            except Exception as e:
                print(f"⚠️ Academic reasoning error: {e}")
                # Fallback to basic RAG answer from knowledge base
                return {
                    "answer": base_answer,
                    "reasoning_type": "fallback_rag",
                    "confidence": 0.5,
                    "academic_quality": "medium",
                    "citations_needed": [],
                    "source_documents": source_documents,
                    "timestamp": "",
                    "reasoning_error": str(e),
                    "knowledge_base_answer": base_answer,
                    "documents_used": len(source_documents)
                }
        else:
            # No reasoning engine available, use basic RAG
            return {
                "answer": base_answer,
                "reasoning_type": "basic_rag",
                "confidence": 0.6,
                "academic_quality": "medium",
                "citations_needed": [],
                "source_documents": source_documents,
                "timestamp": "",
                "knowledge_base_answer": base_answer,
                "documents_used": len(source_documents)
            }
    
    async def generate_literature_summary(self, focus: str = "general", k: int = 15) -> Dict[str, Any]:
        """Generate an academic literature summary from the knowledge base documents"""
        if not self.vectorstore:
            return {"summary": "No documents available in knowledge base for summarization."}
        
        # Get a diverse set of documents from knowledge base
        try:
            # Use a broad query to get diverse content from knowledge base
            query = f"research literature review {focus}"
            relevant_docs = self.retriever.get_relevant_documents(query)
            
            if not relevant_docs:
                # If no specific docs found, try a more general query
                general_docs = self.retriever.get_relevant_documents("research study analysis methodology")
                relevant_docs = general_docs[:k] if general_docs else []
            
            if not relevant_docs:
                return {
                    "summary": f"No relevant documents found in your knowledge base for the focus area '{focus}'. Please upload relevant academic documents first.",
                    "document_count": 0,
                    "focus_area": focus,
                    "academic_quality": "low",
                    "timestamp": "",
                    "source_documents": [],
                    "error": "No documents in knowledge base"
                }
            
            if self.reasoning_enabled and relevant_docs:
                # Enhanced focus that emphasizes knowledge base
                enhanced_focus = f"{focus} - based strictly on the documents in the knowledge base"
                
                summary_result = await reasoning_engine.generate_academic_summary(
                    relevant_docs, enhanced_focus
                )
                
                # Add knowledge base context to summary
                if summary_result.get("summary"):
                    original_summary = summary_result["summary"]
                    summary_result["summary"] = f"""**Literature Summary from Your Knowledge Base:**

{original_summary}

**Note:** This summary is based on {len(relevant_docs)} documents from your knowledge base. For a more comprehensive review, consider uploading additional relevant academic sources."""
                
                summary_result["knowledge_base_documents"] = len(relevant_docs)
                summary_result["source_documents"] = relevant_docs  # Include source documents
                return summary_result
            else:
                return {
                    "summary": f"Reasoning engine not available. Found {len(relevant_docs)} relevant documents in knowledge base for '{focus}' but cannot generate detailed summary.",
                    "document_count": len(relevant_docs),
                    "focus_area": focus,
                    "knowledge_base_documents": len(relevant_docs),
                    "source_documents": relevant_docs
                }
                
        except Exception as e:
            return {
                "summary": f"Error generating literature summary from knowledge base: {str(e)}",
                "document_count": 0,
                "focus_area": focus,
                "source_documents": [],
                "error": str(e)
            }
    
    def _combine_rag_and_reasoning(self, rag_answer: str, reasoning: str) -> str:
        """Combine RAG answer with academic reasoning"""
        if not reasoning or reasoning.strip() == "":
            return rag_answer
        
        combined = f"""**Direct Answer:**
{rag_answer}

**Academic Analysis:**
{reasoning}"""
        
        return combined
    
    async def delete_document(self, document_id: str):
        """Delete all chunks of a document from vector store"""
        # This is a limitation of FAISS - we need to rebuild the index
        # For production, consider using a vector DB with delete support
        print(f"⚠️ Document deletion requires rebuilding index (FAISS limitation)")
        # TODO: Implement by filtering and rebuilding
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_vectors": self.vectorstore.index.ntotal if self.vectorstore else 0,
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.LLM_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "reasoning_enabled": self.reasoning_enabled,
            "reasoning_model": settings.REASONING_MODEL if self.reasoning_enabled else None,
            "reasoning_provider": "OpenRouter AI (DeepSeek)" if self.reasoning_enabled else None
        }


# Global instance
rag_engine = RAGEngine()
