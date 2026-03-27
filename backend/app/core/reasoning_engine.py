import os
import json
import httpx
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
import re
from datetime import datetime

from app.core.config import settings


class AcademicReasoningEngine:
    """
    Advanced reasoning engine using OpenRouter AI's DeepSeek model optimized for academic research.
    Provides multi-step reasoning, citation analysis, and academic writing assistance.
    """
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.REASONING_MODEL
        self.max_tokens = settings.REASONING_MAX_TOKENS
        self.temperature = settings.REASONING_TEMPERATURE
        
        # Academic reasoning templates
        self.reasoning_templates = {
            "research_analysis": """
You are an expert academic researcher. Analyze the following research question using ONLY the information provided in the context documents. Do not use external knowledge.

Research Question: {question}

Context Documents from Knowledge Base:
{context}

IMPORTANT: Base your analysis STRICTLY on the provided documents. If information is not available in the documents, clearly state this limitation.

Please provide a comprehensive analysis following this structure:
1. **Problem Definition**: Clearly state the research problem based on the documents
2. **Literature Review**: Summarize key findings ONLY from the provided documents
3. **Critical Analysis**: Evaluate methodologies and evidence quality from the documents
4. **Synthesis**: Connect findings across the provided sources
5. **Implications**: Discuss implications based on the document content
6. **Limitations**: Note what information is missing from the provided documents
7. **Future Directions**: Suggest areas for further research based on gaps in the documents

Analysis based on provided documents:""",

            "methodology_review": """
You are a methodology expert reviewing research approaches. Analyze ONLY the methodological information present in the provided documents.

Research Focus: {question}

Documents from Knowledge Base:
{context}

IMPORTANT: Review ONLY the methodologies described in the provided documents. Do not suggest methodologies not mentioned in these sources.

Provide a detailed methodological analysis:
1. **Research Design**: Identify research designs mentioned in the documents
2. **Data Collection**: Assess data collection methods described in the documents
3. **Analysis Techniques**: Review analytical approaches found in the documents
4. **Validity & Reliability**: Evaluate validity based on information in the documents
5. **Limitations**: Identify methodological limitations mentioned in the documents
6. **Document Gaps**: Note methodological information not covered in the provided sources

Methodological Analysis based on provided documents:""",

            "literature_synthesis": """
You are conducting a literature review using ONLY the provided academic sources. Do not include external literature not present in the documents.

Topic: {question}

Sources from Knowledge Base:
{context}

IMPORTANT: Synthesize ONLY the literature provided in these documents. Do not reference external sources or general knowledge.

Provide a comprehensive literature synthesis:
1. **Thematic Organization**: Group findings by themes present in the provided documents
2. **Theoretical Frameworks**: Identify theories mentioned in the provided sources
3. **Empirical Evidence**: Summarize evidence ONLY from the provided documents
4. **Consensus & Debates**: Highlight agreements/disagreements within the provided sources
5. **Evolution of Ideas**: Trace development based on the provided documents
6. **Research Gaps**: Identify gaps based on what's missing from the provided literature

Literature Synthesis based on provided sources:""",

            "critical_evaluation": """
You are a peer reviewer evaluating academic work. Provide analysis based STRICTLY on the provided materials.

Research Question: {question}

Materials from Knowledge Base:
{context}

IMPORTANT: Evaluate ONLY based on the information in the provided documents. Do not apply external standards not mentioned in these sources.

Conduct a thorough critical evaluation:
1. **Strengths**: Identify strengths mentioned or evident in the documents
2. **Weaknesses**: Point out limitations described in the documents
3. **Evidence Quality**: Assess evidence quality based on the provided information
4. **Logical Consistency**: Evaluate consistency within the provided documents
5. **Originality**: Assess contributions based on what's presented in the documents
6. **Missing Information**: Note what information would be needed for complete evaluation

Critical Evaluation based on provided materials:""",

            "concept_explanation": """
You are an expert educator explaining concepts. Use ONLY the information provided in the reference materials to explain the concept.

Concept/Question: {question}

Reference Materials from Knowledge Base:
{context}

IMPORTANT: Explain the concept using ONLY the information in the provided materials. If the materials don't contain sufficient information, clearly state this limitation.

Provide a comprehensive explanation:
1. **Definition**: Define concepts based on the provided materials
2. **Context**: Provide context based on information in the documents
3. **Key Components**: Break down concepts using information from the sources
4. **Examples**: Use examples ONLY from the provided materials
5. **Relationships**: Show connections based on the provided documents
6. **Limitations**: Note what aspects are not covered in the provided materials

Explanation based on provided materials:""",

            "research_proposal": """
You are helping develop a research proposal using the provided literature as background. Base recommendations ONLY on the provided sources.

Research Interest: {question}

Background Literature from Knowledge Base:
{context}

IMPORTANT: Develop the proposal framework using ONLY the background provided in these documents. Clearly note where additional literature would be needed.

Develop a research proposal framework:
1. **Background & Rationale**: Establish need based on the provided literature
2. **Research Questions**: Formulate questions based on gaps in the provided sources
3. **Theoretical Framework**: Use theories mentioned in the provided documents
4. **Methodology**: Propose methods based on approaches in the provided literature
5. **Expected Contributions**: Articulate contributions relative to the provided sources
6. **Literature Gaps**: Identify additional sources needed for complete proposal

Research Proposal Framework based on provided literature:"""
        }
    
    async def initialize(self):
        """Initialize the OpenRouter AI client"""
        print("🧠 Initializing OpenRouter AI DeepSeek reasoning engine...")
        
        # Get API key from environment
        self.api_key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file or environment variables."
            )
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/your-repo",  # Optional
                "X-Title": settings.OPENROUTER_APP_NAME,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # Test the connection
        try:
            await self._test_connection()
            print(f"✅ OpenRouter AI DeepSeek reasoning engine initialized successfully")
            print(f"   Model: {self.model}")
            print(f"   Max Tokens: {self.max_tokens}")
            print(f"   Temperature: {self.temperature}")
            
        except Exception as e:
            print(f"⚠️ Failed to connect to OpenRouter AI: {e}")
            raise
    
    async def _test_connection(self):
        """Test the OpenRouter AI connection"""
        test_payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "Hello, this is a connection test."}
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = await self.client.post("/chat/completions", json=test_payload)
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API test failed: {response.status_code} - {response.text}")
        
        result = response.json()
        if "choices" not in result or not result["choices"]:
            raise Exception("Invalid response format from OpenRouter API")
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents for academic context"""
        formatted_docs = []
        
        for i, doc in enumerate(documents, 1):
            # Extract metadata
            source = doc.metadata.get('source', 'Unknown')
            chunk_id = doc.metadata.get('chunk_id', f'chunk_{i}')
            
            # Clean and format content
            content = doc.page_content.strip()
            if len(content) > 1200:
                content = content[:1200] + "..."
            
            formatted_doc = f"""
Document {i} (Source: {source}):
{content}
---"""
            formatted_docs.append(formatted_doc)
        
        return "\n".join(formatted_docs)
    
    def _detect_reasoning_type(self, question: str) -> str:
        """Detect the type of academic reasoning needed based on the question"""
        question_lower = question.lower()
        
        # Keywords for different reasoning types
        methodology_keywords = ['method', 'methodology', 'approach', 'design', 'analysis', 'statistical', 'qualitative', 'quantitative']
        literature_keywords = ['review', 'literature', 'synthesis', 'summary', 'overview', 'survey']
        critical_keywords = ['evaluate', 'critique', 'assess', 'analyze', 'critical', 'strengths', 'weaknesses']
        concept_keywords = ['explain', 'define', 'what is', 'concept', 'theory', 'principle']
        proposal_keywords = ['research proposal', 'study design', 'investigate', 'research question']
        
        # Check for matches
        if any(keyword in question_lower for keyword in methodology_keywords):
            return "methodology_review"
        elif any(keyword in question_lower for keyword in literature_keywords):
            return "literature_synthesis"
        elif any(keyword in question_lower for keyword in critical_keywords):
            return "critical_evaluation"
        elif any(keyword in question_lower for keyword in concept_keywords):
            return "concept_explanation"
        elif any(keyword in question_lower for keyword in proposal_keywords):
            return "research_proposal"
        else:
            return "research_analysis"  # Default
    
    async def reason(self, question: str, context_documents: List[Document]) -> Dict[str, Any]:
        """
        Perform academic reasoning on the question using retrieved context
        """
        if not self.client:
            raise RuntimeError("Reasoning engine not initialized")
        
        # Detect reasoning type
        reasoning_type = self._detect_reasoning_type(question)
        
        # Format context
        formatted_context = self._format_context(context_documents)
        
        # Get appropriate template
        template = self.reasoning_templates[reasoning_type]
        
        # Create prompt
        prompt = template.format(
            question=question,
            context=formatted_context
        )
        
        try:
            # Prepare the API request
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert academic researcher and educator. Provide thorough, well-structured, and evidence-based academic analysis. Always maintain scholarly rigor and objectivity."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            # Make the API call
            response = await self.client.post("/chat/completions", json=payload)
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise Exception("Invalid response format from OpenRouter API")
            
            # Extract generated text
            reasoning_output = result["choices"][0]["message"]["content"].strip()
            
            # Post-process the output
            reasoning_output = self._post_process_reasoning(reasoning_output)
            
            return {
                "reasoning_type": reasoning_type,
                "reasoning": reasoning_output,
                "confidence": self._calculate_confidence(reasoning_output),
                "academic_quality": self._assess_academic_quality(reasoning_output),
                "citations_needed": self._identify_citation_needs(reasoning_output),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            print(f"Error in reasoning generation: {e}")
            return {
                "reasoning_type": reasoning_type,
                "reasoning": "I apologize, but I encountered an error while processing your academic query. Please try rephrasing your question or check if the OpenRouter API is accessible.",
                "confidence": 0.0,
                "academic_quality": "error",
                "citations_needed": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _post_process_reasoning(self, text: str) -> str:
        """Post-process the reasoning output for better academic formatting"""
        # Remove any incomplete sentences at the end
        sentences = text.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            text = '.'.join(sentences[:-1]) + '.'
        
        # Ensure proper paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Clean up extra whitespace
        text = re.sub(r' +', ' ', text)
        
        # Ensure proper formatting for numbered lists
        text = re.sub(r'\n(\d+\.)', r'\n\n\1', text)
        
        return text.strip()
    
    def _calculate_confidence(self, reasoning: str) -> float:
        """Calculate confidence score based on reasoning quality indicators"""
        confidence_indicators = {
            'specific_citations': len(re.findall(r'Document \d+', reasoning)) * 0.1,
            'structured_response': 1.0 if any(marker in reasoning for marker in ['1.', '2.', '**', 'Analysis:', 'Conclusion:']) else 0.0,
            'academic_language': 0.5 if any(term in reasoning.lower() for term in ['however', 'furthermore', 'therefore', 'consequently', 'evidence suggests']) else 0.0,
            'length_adequacy': min(len(reasoning) / 800, 1.0) * 0.3,
            'no_errors': 0.2 if 'error' not in reasoning.lower() else 0.0
        }
        
        return min(sum(confidence_indicators.values()), 1.0)
    
    def _assess_academic_quality(self, reasoning: str) -> str:
        """Assess the academic quality of the reasoning"""
        quality_score = 0
        
        # Check for academic structure
        if any(marker in reasoning for marker in ['1.', '**', 'Analysis:', 'Methodology:']):
            quality_score += 2
        
        # Check for critical thinking indicators
        critical_terms = ['however', 'nevertheless', 'on the other hand', 'critically', 'evaluate']
        if any(term in reasoning.lower() for term in critical_terms):
            quality_score += 2
        
        # Check for evidence-based reasoning
        if 'evidence' in reasoning.lower() or 'Document' in reasoning:
            quality_score += 2
        
        # Check length and depth
        if len(reasoning) > 500:
            quality_score += 1
        
        # Check for academic terminology
        academic_terms = ['theoretical', 'empirical', 'methodology', 'framework', 'implications']
        if any(term in reasoning.lower() for term in academic_terms):
            quality_score += 1
        
        if quality_score >= 7:
            return "high"
        elif quality_score >= 4:
            return "medium"
        else:
            return "low"
    
    def _identify_citation_needs(self, reasoning: str) -> List[str]:
        """Identify statements that need citations"""
        citation_patterns = [
            r'studies show',
            r'research indicates',
            r'evidence suggests',
            r'according to',
            r'findings reveal',
            r'data demonstrates',
            r'literature suggests',
            r'previous work',
            r'scholars argue'
        ]
        
        needs_citations = []
        for pattern in citation_patterns:
            matches = re.finditer(pattern, reasoning, re.IGNORECASE)
            for match in matches:
                # Extract sentence containing the pattern
                start = max(0, reasoning.rfind('.', 0, match.start()) + 1)
                end = reasoning.find('.', match.end())
                if end == -1:
                    end = len(reasoning)
                sentence = reasoning[start:end].strip()
                if sentence and sentence not in needs_citations:
                    needs_citations.append(sentence)
        
        return needs_citations
    
    async def generate_academic_summary(self, documents: List[Document], focus: str = "general") -> Dict[str, Any]:
        """Generate an academic summary of the provided documents from knowledge base"""
        if not documents:
            return {"summary": "No documents provided from knowledge base for summarization."}
        
        # Create summary prompt that emphasizes knowledge base
        context = self._format_context(documents)
        
        summary_prompt = f"""
You are an academic researcher creating a scholarly summary. Analyze the following documents from the knowledge base and provide a comprehensive academic summary.

Focus Area: {focus}

Documents from Knowledge Base:
{context}

IMPORTANT: Base your summary STRICTLY on the provided documents from the knowledge base. Do not include external knowledge or information not present in these documents.

Provide a structured academic summary:
1. **Overview**: Main topics and scope covered in the knowledge base documents
2. **Key Findings**: Most important discoveries or insights from the provided sources
3. **Methodological Approaches**: Research methods described in the knowledge base documents
4. **Theoretical Contributions**: Theoretical insights found in the provided sources
5. **Practical Implications**: Applications mentioned in the knowledge base documents
6. **Limitations**: Constraints and limitations noted in the provided documents
7. **Knowledge Base Gaps**: Areas not covered by the current knowledge base documents
8. **Future Research**: Directions suggested by the knowledge base documents

Academic Summary based on knowledge base documents:"""

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert academic researcher specializing in literature reviews and synthesis. Provide comprehensive, well-structured academic summaries based ONLY on the provided documents. Do not use external knowledge."
                    },
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.6,
                "top_p": 0.9
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            summary = self._post_process_reasoning(summary)
            
            return {
                "summary": summary,
                "document_count": len(documents),
                "focus_area": focus,
                "academic_quality": self._assess_academic_quality(summary),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                "knowledge_base_source": True
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary from knowledge base documents: {str(e)}",
                "document_count": len(documents),
                "focus_area": focus,
                "error": str(e),
                "knowledge_base_source": True
            }
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()


# Global instance
reasoning_engine = AcademicReasoningEngine()