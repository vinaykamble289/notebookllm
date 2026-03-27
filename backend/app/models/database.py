"""
SQLite Database using SQLAlchemy
Normalizes data across users, documents, queries, and chat sessions
"""
import os
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import uuid4

from sqlalchemy import create_engine, Column, String, DateTime, Integer, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

from app.core.config import settings
from app.models.schemas import Role, IngestionStatus

# Create database engine
DATABASE_URL = f"sqlite:///{os.path.join(settings.VECTOR_STORE_DIR, 'app.db')}"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    content_type = Column(String)
    ingestion_status = Column(String, default="pending")
    chunk_count = Column(Integer, default=0)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String, ForeignKey("users.id"))
    
    # Relationships
    queries = relationship("Query", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    answer = Column(Text)
    confidence_score = Column(Float)
    processing_time = Column(Float)
    reasoning_enabled = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    document = relationship("Document", back_populates="queries")
    citations = relationship("Citation", back_populates="query", cascade="all, delete-orphan")


class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    query_id = Column(String, ForeignKey("queries.id"), nullable=False)
    title = Column(String)
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_id = Column(String, ForeignKey("document_chunks.id"))
    text_snippet = Column(Text)
    confidence_score = Column(Float)
    download_url = Column(String)
    filename = Column(String)
    
    # Relationships
    query = relationship("Query", back_populates="citations")
    document = relationship("Document")
    chunk = relationship("DocumentChunk")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# Database class for CRUD operations
class Database:
    def __init__(self):
        self.db_path = os.path.join(settings.VECTOR_STORE_DIR, 'app.db')
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        Base.metadata.create_all(bind=engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()
    
    # User operations
    def add_user(self, user_data: dict) -> str:
        """Add a new user"""
        with self.get_session() as session:
            user = User(
                id=str(uuid4()),
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                role=user_data.get("role", "student")
            )
            session.add(user)
            session.commit()
            return user.id
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        with self.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                return self._user_to_dict_with_password(user)
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return self._user_to_dict(user)
            return None
    
    def update_user_role(self, user_id: str, new_role: str):
        """Update user role"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.role = new_role
                session.commit()
    
    def update_user_password(self, user_id: str, new_hash: str):
        """Update user password"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.password_hash = new_hash
                session.commit()
    
    def list_users(self) -> List[dict]:
        """List all users"""
        with self.get_session() as session:
            users = session.query(User).all()
            return [self._user_to_dict(u) for u in users]
    
    # Document operations
    def add_document(self, doc_data: dict) -> str:
        """Add a new document"""
        with self.get_session() as session:
            doc = Document(
                id=str(uuid4()),
                title=doc_data["title"],
                filename=doc_data["filename"],
                file_path=doc_data["file_path"],
                file_size=doc_data.get("file_size"),
                content_type=doc_data.get("content_type"),
                ingestion_status=doc_data.get("ingestion_status", "pending"),
                uploaded_by=doc_data.get("uploaded_by")
            )
            session.add(doc)
            session.commit()
            return doc.id
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """Get document by ID"""
        with self.get_session() as session:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                return self._document_to_dict(doc)
            return None
    
    def list_documents(self, page: int = 1, per_page: int = 10) -> Tuple[List[dict], int]:
        """List documents with pagination"""
        with self.get_session() as session:
            query = session.query(Document).order_by(Document.upload_timestamp.desc())
            total = query.count()
            docs = query.offset((page - 1) * per_page).limit(per_page).all()
            return [self._document_to_dict(d) for d in docs], total
    
    def update_document(self, doc_id: str, updates: dict):
        """Update document"""
        with self.get_session() as session:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                for key, value in updates.items():
                    setattr(doc, key, value)
                session.commit()
    
    def delete_document(self, doc_id: str):
        """Delete document"""
        with self.get_session() as session:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                session.delete(doc)
                session.commit()
    
    # Query operations
    def add_query(self, query_data: dict) -> str:
        """Add a new query"""
        with self.get_session() as session:
            query = Query(
                id=str(uuid4()),
                user_id=query_data["user_id"],
                document_id=query_data.get("document_id"),
                query_text=query_data["query_text"],
                answer=query_data.get("answer"),
                confidence_score=query_data.get("confidence_score"),
                processing_time=query_data.get("processing_time"),
                reasoning_enabled=query_data.get("reasoning_enabled", False)
            )
            session.add(query)
            session.commit()
            return query.id
    
    def get_query(self, query_id: str) -> Optional[dict]:
        """Get query by ID"""
        with self.get_session() as session:
            query = session.query(Query).filter(Query.id == query_id).first()
            if query:
                return self._query_to_dict(query)
            return None
    
    def list_queries(self, page: int = 1, per_page: int = 10) -> Tuple[List[dict], int]:
        """List queries with pagination"""
        with self.get_session() as session:
            query = session.query(Query).order_by(Query.timestamp.desc())
            total = query.count()
            queries = query.offset((page - 1) * per_page).limit(per_page).all()
            return [self._query_to_dict(q) for q in queries], total
    
    # Chat Session operations
    def create_chat_session(self, user_id: str, title: str = "New Chat") -> str:
        """Create a new chat session"""
        with self.get_session() as session:
            chat_session = ChatSession(
                id=str(uuid4()),
                user_id=user_id,
                title=title
            )
            session.add(chat_session)
            session.commit()
            return chat_session.id
    
    def get_chat_session(self, session_id: str) -> Optional[dict]:
        """Get chat session by ID"""
        with self.get_session() as session:
            chat_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if chat_session:
                return self._chat_session_to_dict(chat_session)
            return None
    
    def list_chat_sessions(self, user_id: str) -> List[dict]:
        """List all chat sessions for a user"""
        with self.get_session() as session:
            sessions = session.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(ChatSession.updated_at.desc()).all()
            return [self._chat_session_to_dict(s) for s in sessions]
    
    def add_chat_message(self, session_id: str, role: str, content: str) -> str:
        """Add a message to a chat session"""
        with self.get_session() as session:
            message = ChatMessage(
                id=str(uuid4()),
                session_id=session_id,
                role=role,
                content=content
            )
            session.add(message)
            chat_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if chat_session:
                chat_session.updated_at = datetime.utcnow()
            session.commit()
            return message.id
    
    def get_chat_messages(self, session_id: str) -> List[dict]:
        """Get all messages in a chat session"""
        with self.get_session() as session:
            messages = session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
            return [self._chat_message_to_dict(m) for m in messages]
    
    def delete_chat_session(self, session_id: str):
        """Delete a chat session"""
        with self.get_session() as session:
            session_obj = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session_obj:
                session.delete(session_obj)
                session.commit()
    
    # Helper methods
    def _user_to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _user_to_dict_with_password(self, user: User) -> dict:
        """User dict including password hash for authentication"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _document_to_dict(self, doc: Document) -> dict:
        return {
            "id": doc.id,
            "title": doc.title,
            "filename": doc.filename,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "content_type": doc.content_type,
            "ingestion_status": doc.ingestion_status,
            "chunk_count": doc.chunk_count,
            "upload_timestamp": doc.upload_timestamp.isoformat() if doc.upload_timestamp else None,
            "uploaded_by": doc.uploaded_by
        }
    
    def _query_to_dict(self, query: Query) -> dict:
        return {
            "id": query.id,
            "user_id": query.user_id,
            "document_id": query.document_id,
            "query_text": query.query_text,
            "answer": query.answer,
            "confidence_score": query.confidence_score,
            "processing_time": query.processing_time,
            "reasoning_enabled": query.reasoning_enabled,
            "timestamp": query.timestamp.isoformat() if query.timestamp else None
        }
    
    def _chat_session_to_dict(self, session: ChatSession) -> dict:
        return {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None
        }
    
    def _chat_message_to_dict(self, message: ChatMessage) -> dict:
        return {
            "id": message.id,
            "session_id": message.session_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }


# Global database instance
db = Database()
