import React from 'react';
import { Citation } from '../lib/api';

interface CitationDisplayProps {
  citations: Citation[];
  onDownload?: (citation: Citation) => void;
  title?: string;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed';
}

const CitationDisplay: React.FC<CitationDisplayProps> = ({
  citations,
  onDownload,
  title = "📚 Document Citations",
  className = "",
  variant = 'default'
}) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  const handleDownload = async (citation: Citation) => {
    if (onDownload) {
      try {
        await onDownload(citation);
      } catch (error: any) {
        alert(error.message || 'Failed to download document');
      }
    } else {
      alert('Download functionality not available');
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'compact':
        return {
          container: 'bg-gray-50 border-l-4 border-gray-400',
          item: 'bg-white p-2 rounded border-l-2 border-gray-300',
          title: 'text-gray-700',
          text: 'text-xs'
        };
      case 'detailed':
        return {
          container: 'bg-blue-50 border-l-4 border-blue-500',
          item: 'bg-white p-4 rounded-lg shadow-sm border',
          title: 'text-blue-800',
          text: 'text-sm'
        };
      default:
        return {
          container: 'bg-green-50 border-l-4 border-green-500',
          item: 'bg-white p-3 rounded border',
          title: 'text-green-800',
          text: 'text-sm'
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div className={`mt-6 p-4 ${styles.container} rounded ${className}`}>
      <h4 className={`font-semibold ${styles.title} mb-3`}>
        {title}
      </h4>
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <div key={index} className={styles.item}>
            <div className="flex justify-between items-start mb-2">
              <h5 className="font-medium text-gray-900 flex-1 pr-2">
                {citation.title}
              </h5>
              <div className="flex flex-col items-end space-y-1">
                <span className={`${styles.text} text-gray-500`}>
                  {(citation.confidence_score * 100).toFixed(0)}% confidence
                </span>
                {variant === 'detailed' && citation.document_id && (
                  <span className={`${styles.text} text-gray-400`}>
                    ID: {citation.document_id}
                  </span>
                )}
              </div>
            </div>
            
            {variant !== 'compact' && (
              <p className={`${styles.text} text-gray-600 mb-2 italic leading-relaxed`}>
                "{citation.text_snippet}"
              </p>
            )}
            
            <div className="flex justify-between items-center">
              <span className={`text-xs text-gray-500`}>
                {variant === 'detailed' ? `Chunk: ${citation.chunk_id}` : citation.chunk_id}
              </span>
              
              {citation.download_url && (
                <button
                  onClick={() => handleDownload(citation)}
                  className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2 py-1 rounded transition-colors duration-200 text-sm font-medium flex items-center space-x-1"
                  title={`Download ${citation.filename || 'document'}`}
                >
                  <span>📥</span>
                  <span>
                    {variant === 'compact' ? 'Download' : `Download ${citation.filename || 'Document'}`}
                  </span>
                </button>
              )}
            </div>
            
            {variant === 'detailed' && citation.filename && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <span className="text-xs text-gray-500">
                  File: {citation.filename}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {variant === 'detailed' && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <p className="text-xs text-blue-600">
            {citations.length} source document{citations.length !== 1 ? 's' : ''} referenced
          </p>
        </div>
      )}
    </div>
  );
};

export default CitationDisplay;