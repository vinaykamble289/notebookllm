'use client';

import { useState } from 'react';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { QueryHistory } from '@/components/chat/QueryHistory';
import { MindmapRenderer } from '@/components/chat/MindmapRenderer';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Array<{
    title: string;
    document_id: string;
    chunk_id: string;
    text_snippet: string;
    confidence_score: number;
  }>;
  mindmap?: {
    nodes: Array<{ id: string; label: string; type?: string }>;
    edges: Array<{ from: string; to: string; label?: string }>;
  };
  audio_url?: string;
  // Enhanced reasoning fields
  reasoning_type?: string;
  confidence?: number;
  academic_quality?: string;
  citations_needed?: string[];
  enhanced_answer?: string;
  academic_reasoning?: {
    reasoning_type: string;
    reasoning: string;
    confidence: number;
    academic_quality: string;
    citations_needed: string[];
    timestamp: string;
  };
  processing_time?: number;
  reasoning_enabled?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleNewMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const handleClearHistory = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Academic Assistant</h1>
          <p className="mt-2 text-gray-600">
            Ask questions about uploaded documents and get AI-powered answers with citations
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <QueryHistory 
              messages={messages}
              onClearHistory={handleClearHistory}
            />
          </div>
          
          <div className="lg:col-span-3">
            <ChatInterface
              messages={messages}
              onNewMessage={handleNewMessage}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}