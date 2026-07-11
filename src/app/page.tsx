'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { MessageSquare, Settings, BookOpen, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <div className="p-4 bg-blue-600 rounded-full">
              <BookOpen className="h-12 w-12 text-white" />
            </div>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI Academic Assistant
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Upload educational documents and get AI-powered answers with citations, 
            mindmaps, and audio responses. Transform your research workflow with 
            intelligent document analysis.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/chat">
              <Button size="lg" className="w-full sm:w-auto">
                <MessageSquare className="h-5 w-5 mr-2" />
                Start Chatting
              </Button>
            </Link>
            
            <Link href="/admin">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                <Settings className="h-5 w-5 mr-2" />
                Admin Dashboard
              </Button>
            </Link>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          <div className="text-center p-6 bg-white rounded-lg shadow-sm border">
            <div className="p-3 bg-blue-100 rounded-full w-fit mx-auto mb-4">
              <Zap className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Citations</h3>
            <p className="text-gray-600">
              Get accurate answers with inline citations linking back to source documents
            </p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-sm border">
            <div className="p-3 bg-green-100 rounded-full w-fit mx-auto mb-4">
              <BookOpen className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Visual Mindmaps</h3>
            <p className="text-gray-600">
              Visualize complex information with automatically generated mindmaps
            </p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-sm border">
            <div className="p-3 bg-purple-100 rounded-full w-fit mx-auto mb-4">
              <MessageSquare className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Audio Responses</h3>
            <p className="text-gray-600">
              Listen to answers with high-quality text-to-speech generation
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}