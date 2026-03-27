'use client';

import React from 'react';
import { documentsApi } from '@/lib/api';
import { ExternalLink, Download } from 'lucide-react';

interface Citation {
  title: string;
  document_id: string;
  chunk_id: string;
  text_snippet: string;
  confidence_score: number;
}

interface CitationDisplayProps {
  citations: Citation[];
}

export const CitationDisplay: React.FC<CitationDisplayProps> = ({ citations }) => {
  const handleDownloadDocument = async (documentId: string, title: string) => {
    try {
      const response = await documentsApi.download(documentId);
      const url = response.data.download_url;
      
      const link = document.createElement('a');
      link.href = url;
      link.download = title;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
      <h4 className="text-sm font-medium text-gray-900">Sources & Citations</h4>
      
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <div key={`${citation.document_id}-${citation.chunk_id}`} className="bg-white rounded-md p-3 border">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="inline-flex items-center justify-center w-5 h-5 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                    {index + 1}
                  </span>
                  <h5 className="text-sm font-medium text-gray-900 truncate">
                    {citation.title}
                  </h5>
                </div>
                
                <div className="flex items-center space-x-2 text-xs text-gray-500 mb-2">
                  <span>Confidence: {Math.round(citation.confidence_score * 100)}%</span>
                  <span>•</span>
                  <span>Chunk ID: {citation.chunk_id.slice(0, 8)}...</span>
                </div>
              </div>
              
              <button
                onClick={() => handleDownloadDocument(citation.document_id, citation.title)}
                className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                title="Download document"
              >
                <Download className="h-4 w-4" />
              </button>
            </div>
            
            <blockquote className="text-sm text-gray-700 italic border-l-3 border-blue-200 pl-3 bg-blue-50 rounded-r p-2">
              "{citation.text_snippet}"
            </blockquote>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-gray-500 pt-2 border-t">
        <p>Click the download icon to access the full source document.</p>
      </div>
    </div>
  );
};