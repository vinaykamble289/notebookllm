#!/usr/bin/env python3
"""
Test script for the Academic Reasoning Engine with OpenRouter AI DeepSeek
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.reasoning_engine import reasoning_engine
from langchain.schema import Document


async def test_reasoning_engine():
    """Test the reasoning engine with sample academic content"""
    
    print("🧪 Testing Academic Reasoning Engine (OpenRouter AI DeepSeek)")
    print("=" * 60)
    
    # Check for API key
    api_key = "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"
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ OpenRouter API key found: {api_key[:8]}...")
    
    # Initialize the reasoning engine
    try:
        await reasoning_engine.initialize()
        print("✅ Reasoning engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize reasoning engine: {e}")
        return False
    
    # Create sample academic documents
    sample_docs = [
        Document(
            page_content="""
            This study examines the effectiveness of machine learning algorithms in natural language processing tasks. 
            We conducted experiments using transformer-based models on a dataset of 10,000 academic papers. 
            The results show that BERT-based models achieve 92% accuracy in text classification tasks, 
            while GPT-based models excel in text generation with a BLEU score of 0.85. 
            The methodology involved fine-tuning pre-trained models on domain-specific data.
            Statistical significance was established using t-tests with p < 0.05.
            """,
            metadata={"source": "ML_NLP_Study_2024.pdf", "document_id": "doc1"}
        ),
        Document(
            page_content="""
            Recent advances in artificial intelligence have transformed academic research methodologies. 
            Traditional statistical approaches are being supplemented with deep learning techniques. 
            However, challenges remain in interpretability and reproducibility of AI-driven research. 
            This paper proposes a framework for transparent AI research that includes explainable AI methods 
            and standardized evaluation protocols. The framework was validated across three different domains:
            healthcare, finance, and education. Cross-validation showed consistent performance improvements.
            """,
            metadata={"source": "AI_Research_Framework_2024.pdf", "document_id": "doc2"}
        ),
        Document(
            page_content="""
            The ethical implications of AI in academic research require careful consideration. 
            Issues include data privacy, algorithmic bias, and the potential for AI to replace human judgment.
            A survey of 500 researchers revealed concerns about AI transparency and accountability.
            The study recommends establishing ethical guidelines and review boards for AI research.
            Institutional review boards should be expanded to include AI ethics expertise.
            """,
            metadata={"source": "AI_Ethics_Research_2024.pdf", "document_id": "doc3"}
        )
    ]
    
    # Test different types of academic reasoning
    test_queries = [
        ("What are the main findings about machine learning in NLP?", "research_analysis"),
        ("Evaluate the methodology used in these studies", "methodology_review"),
        ("Explain the concept of transformer-based models", "concept_explanation"),
        ("What are the limitations of current AI research approaches?", "critical_evaluation"),
        ("Synthesize the literature on AI in academic research", "literature_synthesis")
    ]
    
    for i, (query, expected_type) in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/5: {query}")
        print(f"Expected Type: {expected_type}")
        print("-" * 50)
        
        try:
            result = await reasoning_engine.reason(query, sample_docs)
            
            print(f"✅ Reasoning Type: {result['reasoning_type']}")
            print(f"✅ Confidence: {result['confidence']:.2f}")
            print(f"✅ Academic Quality: {result['academic_quality']}")
            print(f"✅ Citations Needed: {len(result['citations_needed'])}")
            print(f"✅ Model Used: {result.get('model_used', 'N/A')}")
            print(f"✅ Tokens Used: {result.get('tokens_used', 'N/A')}")
            print(f"✅ Reasoning Preview: {result['reasoning'][:200]}...")
            
            if result['citations_needed']:
                print(f"📝 Sample Citation Need: {result['citations_needed'][0][:100]}...")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return False
    
    # Test literature summary
    print(f"\n📚 Testing Literature Summary Generation")
    print("-" * 50)
    
    try:
        summary_result = await reasoning_engine.generate_academic_summary(
            sample_docs, 
            focus="machine learning and AI research ethics"
        )
        
        print(f"✅ Document Count: {summary_result['document_count']}")
        print(f"✅ Focus Area: {summary_result['focus_area']}")
        print(f"✅ Academic Quality: {summary_result.get('academic_quality', 'N/A')}")
        print(f"✅ Model Used: {summary_result.get('model_used', 'N/A')}")
        print(f"✅ Tokens Used: {summary_result.get('tokens_used', 'N/A')}")
        print(f"✅ Summary Preview: {summary_result['summary'][:300]}...")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return False
    
    # Cleanup
    try:
        await reasoning_engine.close()
        print(f"\n✅ Reasoning engine closed properly")
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"OpenRouter AI DeepSeek reasoning engine is working properly.")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_reasoning_engine())
    if success:
        print("\n🚀 Ready to use the Academic Reasoning Engine!")
        print("Next steps:")
        print("1. Start the backend: cd backend && python main.py")
        print("2. Upload academic documents")
        print("3. Try academic queries with reasoning")
    else:
        print("\n❌ Tests failed. Please check the configuration and try again.")
    
    sys.exit(0 if success else 1)