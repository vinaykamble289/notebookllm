import React from 'react';
import CitationDisplay from './CitationDisplay';
import { Citation } from '../lib/api';

interface QueryResultsProps {
  result: any;
  queryMode: 'standard' | 'academic' | 'literature';
  onDownload?: (citation: Citation) => void;
  className?: string;
}

const QueryResults: React.FC<QueryResultsProps> = ({
  result,
  queryMode,
  onDownload,
  className = ""
}) => {
  if (!result) return null;

  const isAcademic = queryMode === 'academic';
  const isLiterature = queryMode === 'literature';
  const isStandard = queryMode === 'standard';

  // Render quality badges
  const renderQualityBadges = () => (
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
      {result.reasoning_enabled && (
        <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
          🧠 Reasoning enabled
        </span>
      )}
    </div>
  );

  // Render metadata
  const renderMetadata = () => (
    <div className="mb-4 text-sm text-gray-600 space-y-1">
      {result.reasoning_type && (
        <div>
          <strong>Reasoning Type:</strong> {result.reasoning_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
        </div>
      )}
      {result.processing_time && (
        <div>
          <strong>Processing Time:</strong> {result.processing_time.toFixed(2)}s
        </div>
      )}
      {result.documents_used !== undefined && (
        <div>
          <strong>Documents Used:</strong> {result.documents_used}
        </div>
      )}
      {result.document_count !== undefined && (
        <div>
          <strong>Documents Analyzed:</strong> {result.document_count}
        </div>
      )}
      {result.focus_area && (
        <div>
          <strong>Focus Area:</strong> {result.focus_area}
        </div>
      )}
      {result.knowledge_base_used !== undefined && (
        <div>
          <strong>Knowledge Base Used:</strong> {result.knowledge_base_used ? 'Yes' : 'No'}
        </div>
      )}
    </div>
  );

  // Render citations needed
  const renderCitationsNeeded = () => {
    if (!result.citations_needed || result.citations_needed.length === 0) return null;
    
    return (
      <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
        <h4 className="font-semibold text-yellow-800 mb-3">📝 Statements Needing Citations</h4>
        <ul className="space-y-1">
          {result.citations_needed.map((statement: string, index: number) => (
            <li key={index} className="text-sm text-yellow-700">
              • {statement}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  // Render additional content sections
  const renderAdditionalSections = () => (
    <>
      {/* Enhanced answer for standard queries */}
      {result.enhanced_answer && (
        <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <h4 className="font-semibold text-blue-800 mb-2">🧠 Enhanced Analysis</h4>
          <div className="whitespace-pre-wrap text-blue-700 leading-relaxed">
            {result.enhanced_answer}
          </div>
        </div>
      )}

      {/* Knowledge base answer */}
      {result.knowledge_base_answer && (
        <div className="mt-4 p-4 bg-gray-50 border-l-4 border-gray-500 rounded">
          <h4 className="font-semibold text-gray-800 mb-2">📖 Knowledge Base Answer</h4>
          <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
            {result.knowledge_base_answer}
          </div>
        </div>
      )}

      {/* Academic reasoning details */}
      {result.academic_reasoning && (
        <div className="mt-4 p-4 bg-purple-50 border-l-4 border-purple-500 rounded">
          <h4 className="font-semibold text-purple-800 mb-2">🔬 Academic Reasoning Details</h4>
          <div className="space-y-2 text-sm">
            <div>
              <strong>Type:</strong> {result.academic_reasoning.reasoning_type.replace(/_/g, ' ')}
            </div>
            <div>
              <strong>Confidence:</strong> {(result.academic_reasoning.confidence * 100).toFixed(0)}%
            </div>
            <div>
              <strong>Quality:</strong> {result.academic_reasoning.academic_quality}
            </div>
            {result.academic_reasoning.reasoning && (
              <div className="mt-3 p-3 bg-white rounded border">
                <div className="whitespace-pre-wrap text-purple-700 leading-relaxed">
                  {result.academic_reasoning.reasoning}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mindmap */}
      {result.mindmap && (
        <div className="mt-4 p-4 bg-indigo-50 border-l-4 border-indigo-500 rounded">
          <h4 className="font-semibold text-indigo-800 mb-2">🗺️ Mindmap</h4>
          <div className="text-sm text-indigo-700">
            <div>Nodes: {result.mindmap.nodes?.length || 0}</div>
            <div>Edges: {result.mindmap.edges?.length || 0}</div>
            <p className="mt-2 text-xs">Mindmap visualization would be rendered here</p>
          </div>
        </div>
      )}

      {/* Audio */}
      {result.audio_url && (
        <div className="mt-4 p-4 bg-green-50 border-l-4 border-green-500 rounded">
          <h4 className="font-semibold text-green-800 mb-2">🔊 Audio Response</h4>
          <audio controls className="w-full">
            <source src={result.audio_url} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </>
  );

  return (
    <div className={`mt-6 p-6 bg-white border rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {isAcademic && '🎓 Academic Analysis'}
          {isLiterature && '📚 Literature Summary'}
          {isStandard && '💬 Query Response'}
        </h3>
        {renderQualityBadges()}
      </div>

      {/* Metadata */}
      {renderMetadata()}

      {/* Main content */}
      <div className="prose max-w-none">
        <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
          {result.answer || result.summary}
        </div>
      </div>

      {/* Additional sections */}
      {renderAdditionalSections()}

      {/* Citations */}
      {result.citations && result.citations.length > 0 && (
        <CitationDisplay
          citations={result.citations}
          onDownload={onDownload}
          variant="detailed"
        />
      )}

      {/* Citations needed */}
      {renderCitationsNeeded()}

      {/* Error information */}
      {result.reasoning_error && (
        <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded">
          <h4 className="font-semibold text-red-800 mb-2">⚠️ Reasoning Error</h4>
          <div className="text-sm text-red-700">
            {result.reasoning_error}
          </div>
        </div>
      )}

      {/* Timestamp */}
      {result.timestamp && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Generated: {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default QueryResults;