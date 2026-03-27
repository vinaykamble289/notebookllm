'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { 
  queryApi, 
  QueryRequest, 
  AcademicQueryRequest, 
  LiteratureSummaryRequest,
  ReasoningType 
} from '@/lib/api';
import { ChatMessage } from '@/app/chat/page';
import { MessageBubble } from './MessageBubble';
import { Send, Loader2, Volume2, Map, Brain, BookOpen, MessageSquare } from 'lucide-react';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onNewMessage: (message: ChatMessage) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

type QueryMode = 'standard' | 'academic' | 'literature';

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onNewMessage,
  isLoading,
  setIsLoading
}) => {
  const [query, setQuery] = useState('');
  const [queryMode, setQueryMode] = useState<QueryMode>('standard');
  const [reasoningType, setReasoningType] = useState('auto');
  const [useReasoning, setUseReasoning] = useState(true);
  const [includeAudio, setIncludeAudio] = useState(false);
  const [includeMindmap, setIncludeMindmap] = useState(false);
  const [kValue, setKValue] = useState(8);
  const [reasoningTypes, setReasoningTypes] = useState<ReasoningType[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };

    onNewMessage(userMessage);
    setIsLoading(true);

    try {
      let response;
      
      switch (queryMode) {
        case 'standard':
          const standardRequest: QueryRequest = {
            query: query.trim(),
            k: kValue,
            use_reasoning: useReasoning,
            reasoning_type: reasoningType,
            include_audio: includeAudio,
            include_mindmap: includeMindmap
          };
          response = await queryApi.submit(standardRequest);
          break;
          
        case 'academic':
          const academicRequest: AcademicQueryRequest = {
            query: query.trim(),
            k: kValue,
            reasoning_type: reasoningType,
            focus_area: 'general'
          };
          response = await queryApi.submitAcademic(academicRequest);
          break;
          
        case 'literature':
          const summaryRequest: LiteratureSummaryRequest = {
            focus: query.trim() || 'general',
            k: kValue
          };
          response = await queryApi.generateSummary(summaryRequest);
          break;
          
        default:
          throw new Error('Invalid query mode');
      }
      
      // Handle different response types
      let content: string;
      let citations: any[] = [];
      let responseData: any = response.data;
      
      if ('summary' in responseData) {
        // Literature summary response
        content = responseData.summary;
      } else {
        // Standard or academic response
        content = responseData.answer;
        citations = responseData.citations || [];
      }
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: content,
        timestamp: new Date(),
        citations: citations,
        mindmap: responseData.mindmap,
        audio_url: responseData.audio_url,
        // Enhanced reasoning fields
        reasoning_type: responseData.reasoning_type,
        confidence: responseData.confidence,
        academic_quality: responseData.academic_quality,
        citations_needed: responseData.citations_needed,
        enhanced_answer: responseData.enhanced_answer,
        academic_reasoning: responseData.academic_reasoning,
        processing_time: responseData.processing_time,
        reasoning_enabled: responseData.reasoning_enabled
      };

      onNewMessage(assistantMessage);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message || 'Please try again later.'}`,
        timestamp: new Date()
      };
      onNewMessage(errorMessage);
    } finally {
      setIsLoading(false);
      setQuery('');
    }
  };

  const getQueryModeIcon = (mode: QueryMode) => {
    switch (mode) {
      case 'standard': return <MessageSquare className="h-4 w-4" />;
      case 'academic': return <Brain className="h-4 w-4" />;
      case 'literature': return <BookOpen className="h-4 w-4" />;
    }
  };

  const getQueryModeLabel = (mode: QueryMode) => {
    switch (mode) {
      case 'standard': return 'Standard Query';
      case 'academic': return 'Academic Analysis';
      case 'literature': return 'Literature Summary';
    }
  };

  const getPlaceholder = () => {
    switch (queryMode) {
      case 'standard': return 'Ask a question about the documents...';
      case 'academic': return 'Enter your academic research question...';
      case 'literature': return 'Enter focus area for literature summary...';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border flex flex-col h-[700px]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Chat with AI Assistant</h2>
        <p className="text-sm text-gray-500 mt-1">
          Ask questions about uploaded documents with advanced reasoning capabilities
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-blue-50 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <Send className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Ask any question about the uploaded documents. Choose from standard queries, academic analysis, or literature summaries.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Query Mode Selection */}
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Query Type:</label>
            <div className="flex space-x-2">
              {(['standard', 'academic', 'literature'] as QueryMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setQueryMode(mode)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    queryMode === mode
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                  }`}
                >
                  {getQueryModeIcon(mode)}
                  <span>{getQueryModeLabel(mode)}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Reasoning Type */}
            {(queryMode === 'academic' || (queryMode === 'standard' && useReasoning)) && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reasoning Type
                </label>
                <select
                  value={reasoningType}
                  onChange={(e) => setReasoningType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
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
            
            {/* K Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Documents (k)
              </label>
              <input
                type="number"
                value={kValue}
                onChange={(e) => setKValue(parseInt(e.target.value) || 8)}
                min="1"
                max="20"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
          </div>

          {/* Options */}
          <div className="flex flex-wrap items-center gap-6">
            {queryMode === 'standard' && (
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={useReasoning}
                  onChange={(e) => setUseReasoning(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <Brain className="h-4 w-4 text-gray-400" />
                <span className="text-gray-700">Use reasoning</span>
              </label>
            )}
            
            {queryMode === 'standard' && (
              <>
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={includeAudio}
                    onChange={(e) => setIncludeAudio(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <Volume2 className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-700">Include audio</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={includeMindmap}
                    onChange={(e) => setIncludeMindmap(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <Map className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-700">Include mindmap</span>
                </label>
              </>
            )}
          </div>

          {/* Input */}
          <div className="flex space-x-3">
            <div className="flex-1">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={getPlaceholder()}
                disabled={isLoading}
                className="border-gray-300 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <Button
              type="submit"
              disabled={!query.trim() || isLoading}
              loading={isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};