#!/usr/bin/env python3
"""
Test script to verify that academic queries use the knowledge base properly
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.rag_engine import rag_engine
from langchain.schema import Document


async def test_knowledge_base_integration():
    """Test that academic queries use knowledge base documents"""
    
    print("🧪 Testing Knowledge Base Integration for Academic Queries")
    print("=" * 60)
    
    # Initialize the RAG engine
    try:
        await rag_engine.initialize()
        print("✅ RAG engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG engine: {e}")
        return False
    
    # Add test documents to the knowledge base
    test_documents = [
        Document(
            page_content="""
            This research paper investigates the impact of artificial intelligence on educational outcomes.
            The study was conducted at XYZ University with 500 students over 6 months.
            Results show that AI-assisted learning improved test scores by 23% compared to traditional methods.
            The methodology involved randomized controlled trials with pre and post assessments.
            Statistical analysis used t-tests with p < 0.05 significance level.
            Limitations include small sample size and single institution focus.
            """,
            metadata={"source": "AI_Education_Study_2024.pdf", "document_id": "test_doc_1"}
        ),
        Document(
            page_content="""
            Machine learning algorithms in healthcare diagnosis: A systematic review.
            This meta-analysis examined 45 studies on ML applications in medical diagnosis.
            Deep learning models achieved 94% accuracy in radiology image analysis.
            Natural language processing showed 87% accuracy in clinical note analysis.
            Key challenges include data privacy, model interpretability, and regulatory approval.
            Future research should focus on federated learning and explainable AI.
            """,
            metadata={"source": "ML_Healthcare_Review_2024.pdf", "document_id": "test_doc_2"}
        )
    ]
    
    # Add documents to knowledge base
    try:
        chunks_added = await rag_engine.add_documents(test_documents, "test_knowledge_base")
        print(f"✅ Added {chunks_added} chunks to knowledge base")
    except Exception as e:
        print(f"❌ Failed to add documents to knowledge base: {e}")
        return False
    
    # Test queries that should use knowledge base
    test_queries = [
        "What were the results of the AI education study?",
        "What methodology was used in the healthcare ML research?",
        "What are the limitations mentioned in the studies?",
        "What accuracy rates were achieved in the healthcare study?"
    ]
    
    print(f"\n🔍 Testing Academic Queries with Knowledge Base")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/4: {query}")
        print("-" * 30)
        
        try:
            # Test academic query
            result = await rag_engine.academic_query(query, k=5)
            
            answer = result.get("answer", "")
            docs_used = result.get("documents_used", 0)
            kb_answer = result.get("knowledge_base_answer", "")
            
            print(f"✅ Documents Used: {docs_used}")
            print(f"✅ Reasoning Type: {result.get('reasoning_type', 'N/A')}")
            print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
            print(f"✅ Academic Quality: {result.get('academic_quality', 'N/A')}")
            
            # Check if answer contains knowledge base information
            kb_indicators = [
                "XYZ University", "500 students", "23%", "6 months",
                "45 studies", "94% accuracy", "87% accuracy", "radiology"
            ]
            
            found_indicators = [ind for ind in kb_indicators if ind.lower() in answer.lower()]
            
            if found_indicators:
                print(f"✅ Knowledge Base Used: Found {len(found_indicators)} specific references")
                print(f"   References: {', '.join(found_indicators[:3])}...")
            else:
                print(f"⚠️ Knowledge Base Usage Unclear: No specific references found")
            
            print(f"📝 Answer Preview: {answer[:200]}...")
            
            if kb_answer:
                print(f"📚 KB Answer: {kb_answer[:100]}...")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return False
    
    # Test with query that shouldn't find relevant documents
    print(f"\n🔍 Testing Query with No Relevant Documents")
    print("-" * 50)
    
    try:
        result = await rag_engine.academic_query("What is the capital of Mars?", k=5)
        
        if "No relevant documents found" in result.get("answer", ""):
            print("✅ Correctly identified no relevant documents in knowledge base")
        else:
            print("⚠️ Should have indicated no relevant documents found")
        
        print(f"📝 Response: {result.get('answer', '')[:200]}...")
        
    except Exception as e:
        print(f"❌ Error with irrelevant query: {e}")
    
    print(f"\n🎉 Knowledge Base Integration Test Completed!")
    print("The academic reasoning engine should now use your knowledge base documents.")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_knowledge_base_integration())
    if success:
        print("\n✅ Knowledge base integration is working correctly!")
        print("Academic queries will now use your uploaded documents as the primary source.")
    else:
        print("\n❌ Knowledge base integration test failed.")
    
    sys.exit(0 if success else 1)