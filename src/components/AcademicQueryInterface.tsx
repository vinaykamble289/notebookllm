import React, { useState, useEffect } from 'react';
import { 
  queryApi, 
  documentsApi, 
  AcademicQueryRequest, 
  AcademicQueryResponse, 
  LiteratureSummaryRequest, 
  LiteratureSummaryResponse,
  QueryRequest,
  QueryResponse,
  ReasoningType,
  Citation 
} from '../lib/api';

interface AcademicQueryInterfaceProps {
  className?: string;
}

type QueryMode = 'standard' | 'academic' | 'literature';

const AcademicQueryInterface: React.FC<AcademicQueryInterfaceProps> = ({ className = '' }) => {
  // State management
  const [query, setQuery] = useState('');
  const [queryMode, setQueryMode] = useState<QueryMode>('academic');
  const [reasoningType, setReasoningType] = useState('auto');
  const [focusArea, setFocusArea] = useState('general');
  const [kValue, setKValue] = useState(8);
  const [useReasoning, setUseReasoning] = useState(true);
  const [includeMindmap, setIncludeMindmap] = useState(false);
  const [includeAudio, setIncludeAudio] = useState(false);
  
  // Results state
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Available reasoning types
  const [reasoningTypes, setReasoningTypes] = useState<ReasoningType[]>([]);
  
  // Load reasoning types on component mount
  useEffect(() => {
    const loadReasoningTypes = async () => {
      try {
        const response = await queryApi.getReasoningTypes();
        setReasoningTypes(response.data.reasoning_types);
      } catch (error) {
        console.error('Failed to load reasoning types:', error);
      }
    };
    
    loadReasoningTypes();
  }, []);
  
  // Handle query submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResult(null);
    
    try {
      let response;
      
      switch (queryMode) {
        case 'standard':
          const standardRequest: QueryRequest = {
            query,
            k: kValue,
            use_reasoning: useReasoning,
            reasoning_type: reasoningType,
            include_mindmap: includeMindmap,
            include_audio: includeAudio
          };
          response = await queryApi.submit(standardRequest);
          break;
          
        case 'academic':
          const academicRequest: AcademicQueryRequest = {
            query,
            k: kValue,
            reasoning_type: reasoningType,
            focus_area: focusArea
          };
          response = await queryApi.submitAcademic(academicRequest);
          break;
          
        case 'literature':
          const summaryRequest: LiteratureSummaryRequest = {
            focus: query || focusArea,
            k: kValue
          };
          response = await queryApi.generateSummary(summaryRequest);
          break;
          
        default:
          throw new Error('Invalid query mode');
      }
      
      setResult(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message || 'Query failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle document download
  const handleDownload = async (citation: Citation) => {
    if (!citation.download_url || !citation.document_id) {
      alert('Download not available for this document');
      return;
    }
    
    try {
      const response = await documentsApi.downloadFile(citation.document_id);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', citation.filename || 'document.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download document');
    }
  };
  
  // Render citations
  const renderCitations = (citations: Citation[]) => {
    if (!citations || citations.length === 0) return null;
    
    return (
      <div className="mt-6 p-4 bg-green-50 border-l-4 border-green-500 rounded">
        <h4 className="font-semibold text-green-800 mb-3">📚 Document Citations</h4>
        <div className="space-y-3">
          {citations.map((citation, index) => (
            <div key={index} className="bg-white p-3 rounded border">
              <div className="flex justify-between items-start mb-2">
                <h5 className="font-medium text-gray-900">{citation.title}</h5>
                <span className="text-sm text-gray-500">
                  {(citation.confidence_score * 100).toFixed(0)}% confidence
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2 italic">
                "{citation.text_snippet}"
              </p>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  Chunk: {citation.chunk_id}
                </span>
                {citation.download_url && (
                  <button
                    onClick={() => handleDownload(citation)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                  >
                    📥 Download {citation.filename || 'Document'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  // Render citations needed
  const renderCitationsNeeded = (citationsNeeded: string[]) => {
    if (!citationsNeeded || citationsNeeded.length === 0) return null;
    
    return (
      <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
        <h4 className="font-semibold text-yellow-800 mb-3">📝 Statements Needing Citations</h4>
        <ul className="space-y-1">
          {citationsNeeded.map((statement, index) => (
            <li key={index} className="text-sm text-yellow-700">
              • {statement}
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  // Render results based on query mode
  const renderResults = () => {
    if (!result) return null;
    
    const isAcademic = queryMode === 'academic';
    const isLiterature = queryMode === 'literature';
    const isStandard = queryMode === 'standard';
    
    return (
      <div className="mt-6 p-6 bg-white border rounded-lg shadow">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {isAcademic && '🎓 Academic Analysis'}
            {isLiterature && '📚 Literature Summary'}
            {isStandard && '💬 Query Response'}
          </h3>
          <div className="flex space-x-2">
            {result.confidence !== undefined && (
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                result.confidence >= 0.7 ? 'bg-green-100 text-green-800' :
                result.confidence >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {(result.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
            {result.academic_quality && (
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                result.academic_quality === 'high' ? 'bg-blue-100 text-blue-800' :
                result.academic_quality === 'medium' ? 'bg-gray-100 text-gray-800' :
                'bg-red-100 text-red-800'
              }`}>
                {result.academic_quality} quality
              </span>
            )}
          </div>
        </div>
        
        {/* Metadata */}
        <div className="mb-4 text-sm text-gray-600 space-y-1">
          {result.reasoning_type && (
            <div><strong>Reasoning Type:</strong> {result.reasoning_type.replace('_', ' ')}</div>
          )}
          {result.processing_time && (
            <div><strong>Processing Time:</strong> {result.processing_time.toFixed(2)}s</div>
          )}
          {result.documents_used !== undefined && (
            <div><strong>Documents Used:</strong> {result.documents_used}</div>
          )}
          {result.document_count !== undefined && (
            <div><strong>Documents Analyzed:</strong> {result.document_count}</div>
          )}
        </div>
        
        {/* Main content */}
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-gray-800">
            {result.answer || result.summary}
          </div>
        </div>
        
        {/* Enhanced answer for standard queries */}
        {result.enhanced_answer && (
          <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <h4 className="font-semibold text-blue-800 mb-2">🧠 Enhanced Analysis</h4>
            <div className="whitespace-pre-wrap text-blue-700">
              {result.enhanced_answer}
            </div>
          </div>
        )}
        
        {/* Knowledge base answer */}
        {result.knowledge_base_answer && (
          <div className="mt-4 p-4 bg-gray-50 border-l-4 border-gray-500 rounded">
            <h4 className="font-semibold text-gray-800 mb-2">📖 Knowledge Base Answer</h4>
            <div className="whitespace-pre-wrap text-gray-700">
              {result.knowledge_base_answer}
            </div>
          </div>
        )}
        
        {/* Citations */}
        {renderCitations(result.citations)}
        
        {/* Citations needed */}
        {renderCitationsNeeded(result.citations_needed)}
        
        {/* Academic reasoning details */}
        {result.academic_reasoning && (
          <div className="mt-4 p-4 bg-purple-50 border-l-4 border-purple-500 rounded">
            <h4 className="font-semibold text-purple-800 mb-2">🔬 Academic Reasoning Details</h4>
            <div className="space-y-2 text-sm">
              <div><strong>Type:</strong> {result.academic_reasoning.reasoning_type}</div>
              <div><strong>Confidence:</strong> {(result.academic_reasoning.confidence * 100).toFixed(0)}%</div>
              <div><strong>Quality:</strong> {result.academic_reasoning.academic_quality}</div>
            </div>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className={`max-w-4xl mx-auto p-6 ${className}`}>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          🧠 Academic Reasoning Engine
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Query Mode Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Query Mode
            </label>
            <div className="flex space-x-4">
              {[
                { value: 'standard', label: '💬 Standard Query', desc: 'Regular query with optional reasoning' },
                { value: 'academic', label: '🎓 Academic Query', desc: 'Specialized academic analysis' },
                { value: 'literature', label: '📚 Literature Summary', desc: 'Generate literature review' }
              ].map((mode) => (
                <label key={mode.value} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    value={mode.value}
                    checked={queryMode === mode.value}
                    onChange={(e) => setQueryMode(e.target.value as QueryMode)}
                    className="text-blue-600"
                  />
                  <div>
                    <div className="font-medium">{mode.label}</div>
                    <div className="text-xs text-gray-500">{mode.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
          
          {/* Query Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {queryMode === 'literature' ? 'Focus Area' : 'Query'}
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                queryMode === 'academic' ? 'Enter your academic research question...' :
                queryMode === 'literature' ? 'Enter focus area for literature summary...' :
                'Enter your query...'
              }
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              required
            />
          </div>
          
          {/* Advanced Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Reasoning Type */}
            {(queryMode === 'academic' || (queryMode === 'standard' && useReasoning)) && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reasoning Type
                </label>
                <select
                  value={reasoningType}
                  onChange={(e) => setReasoningType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="auto">Auto-detect</option>
                  {reasoningTypes.map((type) => (
                    <option key={type.type} value={type.type}>
                      {type.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            {/* Focus Area for Academic */}
            {queryMode === 'academic' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Focus Area
                </label>
                <input
                  type="text"
                  value={focusArea}
                  onChange={(e) => setFocusArea(e.target.value)}
                  placeholder="e.g., machine learning, healthcare"
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
            
            {/* K Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Documents to Retrieve (k)
              </label>
              <input
                type="number"
                value={kValue}
                onChange={(e) => setKValue(parseInt(e.target.value))}
                min="1"
                max="20"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          {/* Standard Query Options */}
          {queryMode === 'standard' && (
            <div className="flex flex-wrap gap-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={useReasoning}
                  onChange={(e) => setUseReasoning(e.target.checked)}
                  className="text-blue-600"
                />
                <span className="text-sm">Use Academic Reasoning</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={includeMindmap}
                  onChange={(e) => setIncludeMindmap(e.target.checked)}
                  className="text-blue-600"
                />
                <span className="text-sm">Include Mindmap</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={includeAudio}
                  onChange={(e) => setIncludeAudio(e.target.checked)}
                  className="text-blue-600"
                />
                <span className="text-sm">Include Audio</span>
              </label>
            </div>
          )}
          
          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              <>
                {queryMode === 'academic' && '🎓 Submit Academic Query'}
                {queryMode === 'literature' && '📚 Generate Literature Summary'}
                {queryMode === 'standard' && '💬 Submit Query'}
              </>
            )}
          </button>
        </form>
        
        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <div className="text-red-800">
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}
        
        {/* Results */}
        {renderResults()}
      </div>
    </div>
  );
};

export default AcademicQueryInterface;