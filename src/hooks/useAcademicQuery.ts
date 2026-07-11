import { useState, useCallback } from 'react';
import { 
  queryApi, 
  documentsApi,
  AcademicQueryRequest, 
  AcademicQueryResponse, 
  LiteratureSummaryRequest, 
  LiteratureSummaryResponse,
  QueryRequest,
  QueryResponse,
  Citation 
} from '../lib/api';

export type QueryMode = 'standard' | 'academic' | 'literature';

export interface UseAcademicQueryOptions {
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
}

export const useAcademicQuery = (options: UseAcademicQueryOptions = {}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const submitQuery = useCallback(async (
    query: string,
    mode: QueryMode,
    params: {
      k?: number;
      reasoningType?: string;
      focusArea?: string;
      useReasoning?: boolean;
      includeMindmap?: boolean;
      includeAudio?: boolean;
    } = {}
  ) => {
    if (!query.trim()) {
      const errorMsg = 'Please enter a query';
      setError(errorMsg);
      options.onError?.(errorMsg);
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;

      switch (mode) {
        case 'standard':
          const standardRequest: QueryRequest = {
            query,
            k: params.k || 8,
            use_reasoning: params.useReasoning ?? true,
            reasoning_type: params.reasoningType || 'auto',
            include_mindmap: params.includeMindmap || false,
            include_audio: params.includeAudio || false
          };
          response = await queryApi.submit(standardRequest);
          break;

        case 'academic':
          const academicRequest: AcademicQueryRequest = {
            query,
            k: params.k || 8,
            reasoning_type: params.reasoningType || 'auto',
            focus_area: params.focusArea || 'general'
          };
          response = await queryApi.submitAcademic(academicRequest);
          break;

        case 'literature':
          const summaryRequest: LiteratureSummaryRequest = {
            focus: query || params.focusArea || 'general',
            k: params.k || 15
          };
          response = await queryApi.generateSummary(summaryRequest);
          break;

        default:
          throw new Error('Invalid query mode');
      }

      setResult(response.data);
      options.onSuccess?.(response.data);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Query failed';
      setError(errorMsg);
      options.onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const downloadDocument = useCallback(async (citation: Citation) => {
    if (!citation.download_url || !citation.document_id) {
      throw new Error('Download not available for this document');
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
    } catch (error: any) {
      throw new Error('Failed to download document: ' + (error.message || 'Unknown error'));
    }
  }, []);

  const clearResults = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    isLoading,
    result,
    error,
    submitQuery,
    downloadDocument,
    clearResults
  };
};

export default useAcademicQuery;