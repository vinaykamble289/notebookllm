'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '@/app/chat/page';
import { CitationDisplay } from './CitationDisplay';
import { MindmapRenderer } from './MindmapRenderer';
import { AudioPlayer } from './AudioPlayer';
import { formatDate } from '@/lib/utils';
import { User, Bot, Volume2, Map, FileText } from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showCitations, setShowCitations] = useState(false);
  const [showMindmap, setShowMindmap] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const isUser = message.type === 'user';

  // Check if this is an enhanced response with reasoning data
  const hasReasoningData = (message as any).reasoning_type || (message as any).academic_reasoning || (message as any).enhanced_answer;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center
            ${isUser ? 'bg-blue-600' : 'bg-gray-600'}
          `}>
            {isUser ? (
              <User className="h-4 w-4 text-white" />
            ) : (
              <Bot className="h-4 w-4 text-white" />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`
            inline-block px-4 py-2 rounded-lg max-w-full
            ${isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-900'
            }
          `}>
            {isUser ? (
              <p className="text-sm">{message.content}</p>
            ) : (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    a: ({ href, children }) => (
                      <a 
                        href={href} 
                        className="text-blue-600 hover:text-blue-800 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    )
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Quality Badges for AI responses */}
          {!isUser && hasReasoningData && (
            <div className="flex flex-wrap gap-2 mt-2">
              {(message as any).confidence !== undefined && (
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  (message as any).confidence >= 0.7 ? 'bg-green-100 text-green-800' :
                  (message as any).confidence >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {((message as any).confidence * 100).toFixed(0)}% confidence
                </span>
              )}
              {(message as any).academic_quality && (
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  (message as any).academic_quality === 'high' ? 'bg-blue-100 text-blue-800' :
                  (message as any).academic_quality === 'medium' ? 'bg-gray-100 text-gray-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {(message as any).academic_quality} quality
                </span>
              )}
              {(message as any).reasoning_type && (
                <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  {(message as any).reasoning_type.replace(/_/g, ' ')}
                </span>
              )}
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {formatDate(message.timestamp)}
          </div>

          {/* Assistant Message Extras */}
          {!isUser && (
            <div className="mt-3 space-y-3">
              {/* Enhanced Answer */}
              {(message as any).enhanced_answer && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
                  <h4 className="font-semibold text-blue-800 mb-2 text-sm">🧠 Enhanced Analysis</h4>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{(message as any).enhanced_answer}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Academic Reasoning Details */}
              {(message as any).academic_reasoning && (
                <div className="bg-purple-50 border-l-4 border-purple-500 p-3 rounded">
                  <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="flex items-center space-x-2 text-sm text-purple-800 font-semibold hover:text-purple-900"
                  >
                    <span>🔬 Academic Reasoning Details</span>
                  </button>
                  
                  {showDetails && (
                    <div className="mt-2 space-y-2 text-sm">
                      <div>
                        <strong>Type:</strong> {(message as any).academic_reasoning.reasoning_type.replace(/_/g, ' ')}
                      </div>
                      <div>
                        <strong>Confidence:</strong> {((message as any).academic_reasoning.confidence * 100).toFixed(0)}%
                      </div>
                      <div>
                        <strong>Quality:</strong> {(message as any).academic_reasoning.academic_quality}
                      </div>
                      {(message as any).academic_reasoning.reasoning && (
                        <div className="mt-3 p-3 bg-white rounded border">
                          <div className="prose prose-sm max-w-none">
                            <ReactMarkdown>{(message as any).academic_reasoning.reasoning}</ReactMarkdown>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Citations Needed */}
              {(message as any).citations_needed && (message as any).citations_needed.length > 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3 rounded">
                  <h4 className="font-semibold text-yellow-800 mb-2 text-sm">📝 Statements Needing Citations</h4>
                  <ul className="space-y-1">
                    {(message as any).citations_needed.map((statement: string, index: number) => (
                      <li key={index} className="text-sm text-yellow-700">
                        • {statement}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Citations */}
              {message.citations && message.citations.length > 0 && (
                <div>
                  <button
                    onClick={() => setShowCitations(!showCitations)}
                    className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    <FileText className="h-4 w-4" />
                    <span>{message.citations.length} Citation{message.citations.length !== 1 ? 's' : ''}</span>
                  </button>
                  
                  {showCitations && (
                    <div className="mt-2">
                      <CitationDisplay citations={message.citations} />
                    </div>
                  )}
                </div>
              )}

              {/* Mindmap */}
              {message.mindmap && (
                <div>
                  <button
                    onClick={() => setShowMindmap(!showMindmap)}
                    className="flex items-center space-x-2 text-sm text-green-600 hover:text-green-800"
                  >
                    <Map className="h-4 w-4" />
                    <span>View Mindmap</span>
                  </button>
                  
                  {showMindmap && (
                    <div className="mt-2">
                      <MindmapRenderer mindmapData={message.mindmap} />
                    </div>
                  )}
                </div>
              )}

              {/* Audio */}
              {message.audio_url && (
                <div>
                  <div className="flex items-center space-x-2 text-sm text-purple-600 mb-2">
                    <Volume2 className="h-4 w-4" />
                    <span>Audio Response</span>
                  </div>
                  <AudioPlayer audioUrl={message.audio_url} />
                </div>
              )}

              {/* Processing Time */}
              {(message as any).processing_time && (
                <div className="text-xs text-gray-500">
                  Processing time: {(message as any).processing_time.toFixed(2)}s
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};