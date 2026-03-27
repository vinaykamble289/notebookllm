'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { ChatMessage } from '@/app/chat/page';
import { formatDate } from '@/lib/utils';
import { Trash2, MessageSquare, User, Bot } from 'lucide-react';

interface QueryHistoryProps {
  messages: ChatMessage[];
  onClearHistory: () => void;
}

export const QueryHistory: React.FC<QueryHistoryProps> = ({
  messages,
  onClearHistory
}) => {
  // Group messages by conversation pairs (user question + AI response)
  const conversations = [];
  for (let i = 0; i < messages.length; i += 2) {
    const userMessage = messages[i];
    const aiMessage = messages[i + 1];
    if (userMessage && userMessage.type === 'user') {
      conversations.push({
        id: userMessage.id,
        question: userMessage.content,
        answer: aiMessage?.content || 'No response',
        timestamp: userMessage.timestamp,
        hasCitations: aiMessage?.citations && aiMessage.citations.length > 0,
        hasMindmap: !!aiMessage?.mindmap,
        hasAudio: !!aiMessage?.audio_url
      });
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border h-[700px] flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Chat History</h3>
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearHistory}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-6 text-center">
            <MessageSquare className="h-8 w-8 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No conversations yet</p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className="p-3 rounded-lg border hover:bg-gray-50 transition-colors cursor-pointer"
              >
                {/* Question */}
                <div className="flex items-start space-x-2 mb-2">
                  <div className="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-3 w-3 text-blue-600" />
                  </div>
                  <p className="text-sm text-gray-900 line-clamp-2 flex-1">
                    {conversation.question}
                  </p>
                </div>

                {/* Answer Preview */}
                <div className="flex items-start space-x-2 mb-2">
                  <div className="flex-shrink-0 w-5 h-5 bg-gray-100 rounded-full flex items-center justify-center">
                    <Bot className="h-3 w-3 text-gray-600" />
                  </div>
                  <p className="text-xs text-gray-600 line-clamp-2 flex-1">
                    {conversation.answer.substring(0, 100)}
                    {conversation.answer.length > 100 ? '...' : ''}
                  </p>
                </div>

                {/* Metadata */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {conversation.hasCitations && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        Citations
                      </span>
                    )}
                    {conversation.hasMindmap && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        Mindmap
                      </span>
                    )}
                    {conversation.hasAudio && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        Audio
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-400">
                    {formatDate(conversation.timestamp).split(',')[1]?.trim() || formatDate(conversation.timestamp)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats */}
      {conversations.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-500 text-center">
            {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}
    </div>
  );
};