'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { DocumentMetadata, documentsApi } from '@/lib/api';
import { formatFileSize, formatDate } from '@/lib/utils';
import { 
  FileText, 
  RefreshCw, 
  Play, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Download,
  Loader2
} from 'lucide-react';

interface DocumentListProps {
  documents: DocumentMetadata[];
  loading: boolean;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  loading,
  onRefresh
}) => {
  const [processingDocs, setProcessingDocs] = useState<Set<string>>(new Set());
  
  // Ensure documents is always an array
  const documentList = Array.isArray(documents) ? documents : [];

  const getStatusIcon = (status: DocumentMetadata['ingestion_status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: DocumentMetadata['ingestion_status']) => {
    switch (status) {
      case 'completed':
        return 'Ready';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      default:
        return 'Pending';
    }
  };

  const getStatusColor = (status: DocumentMetadata['ingestion_status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'processing':
        return 'text-blue-600 bg-blue-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const handleTriggerIngestion = async (documentId: string) => {
    setProcessingDocs(prev => new Set(prev).add(documentId));
    
    try {
      await documentsApi.triggerIngestion(documentId);
      // Refresh the list to get updated status
      setTimeout(() => {
        onRefresh();
        setProcessingDocs(prev => {
          const newSet = new Set(prev);
          newSet.delete(documentId);
          return newSet;
        });
      }, 1000);
    } catch (error) {
      console.error('Failed to trigger ingestion:', error);
      setProcessingDocs(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
    }
  };

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      const response = await documentsApi.download(documentId);
      const url = response.data.download_url;
      
      // Create a temporary link to download the file
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">Loading documents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Documents</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={loading}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {documentList.length === 0 ? (
        <div className="p-12 text-center">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents uploaded</h3>
          <p className="text-gray-500">Upload your first document to get started.</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {documentList.map((doc) => (
            <div key={doc.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-2">
                    <FileText className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {doc.title}
                    </h3>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                    <span>{doc.filename}</span>
                    <span>•</span>
                    <span>{formatFileSize(doc.file_size)}</span>
                    <span>•</span>
                    <span>{formatDate(doc.upload_timestamp)}</span>
                    {doc.chunk_count && (
                      <>
                        <span>•</span>
                        <span>{doc.chunk_count} chunks</span>
                      </>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {getStatusIcon(doc.ingestion_status)}
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-medium
                      ${getStatusColor(doc.ingestion_status)}
                    `}>
                      {getStatusText(doc.ingestion_status)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {doc.ingestion_status === 'pending' && (
                    <Button
                      size="sm"
                      onClick={() => handleTriggerIngestion(doc.id)}
                      disabled={processingDocs.has(doc.id)}
                      loading={processingDocs.has(doc.id)}
                    >
                      <Play className="h-4 w-4 mr-1" />
                      Process
                    </Button>
                  )}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(doc.id, doc.filename)}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};