'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Download, RefreshCw, ZoomIn, ZoomOut } from 'lucide-react';
import * as cytoscape from 'cytoscape';

// Dynamic import for mermaid to avoid SSR issues
let mermaid: any = null;

interface MindmapData {
  nodes: Array<{ id: string; label: string; type?: string }>;
  edges: Array<{ from: string; to: string; label?: string }>;
}

interface MindmapRendererProps {
  mindmapData: MindmapData;
}

export const MindmapRenderer: React.FC<MindmapRendererProps> = ({ mindmapData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  // Initialize Mermaid
  useEffect(() => {
    const initMermaid = async () => {
      if (!mermaid) {
        const mermaidModule = await import('mermaid');
        mermaid = mermaidModule.default;
        mermaid.initialize({
          startOnLoad: true,
          theme: 'default',
          securityLevel: 'loose',
          fontFamily: 'Inter, system-ui, sans-serif',
          mindmap: {
            padding: 20,
            maxNodeSizeRatio: 0.9,
          }
        });
      }
    };
    
    initMermaid();
  }, []);

  // Convert mindmap data to Mermaid syntax
  const generateMermaidSyntax = (data: MindmapData): string => {
    try {
      let mermaidCode = 'mindmap\n  root((Central Topic))\n';
      
      // Create a map to track node relationships
      const nodeMap = new Map<string, { label: string; children: string[] }>();
      
      // Initialize all nodes
      data.nodes.forEach(node => {
        nodeMap.set(node.id, { label: node.label, children: [] });
      });
      
      // Build relationships from edges
      data.edges.forEach(edge => {
        const parent = nodeMap.get(edge.from);
        if (parent) {
          parent.children.push(edge.to);
        }
      });
      
      // Find root nodes (nodes that are not children of any other node)
      const childNodes = new Set(data.edges.map(edge => edge.to));
      const rootNodes = data.nodes.filter(node => !childNodes.has(node.id));
      
      // If no clear root structure, use the first node as root
      if (rootNodes.length === 0 && data.nodes.length > 0) {
        rootNodes.push(data.nodes[0]);
      }
      
      // Generate the mindmap structure recursively
      const generateNodeStructure = (nodeId: string, depth: number = 1): string => {
        const node = nodeMap.get(nodeId);
        if (!node) return '';
        
        const indent = '  '.repeat(depth);
        let result = `${indent}${node.label.replace(/[^\w\s]/g, '')}\n`;
        
        // Add children
        node.children.forEach(childId => {
          result += generateNodeStructure(childId, depth + 1);
        });
        
        return result;
      };
      
      // Add root nodes and their children
      rootNodes.forEach(rootNode => {
        mermaidCode += generateNodeStructure(rootNode.id);
      });
      
      return mermaidCode;
    } catch (err) {
      console.error('Error generating Mermaid syntax:', err);
      return 'mindmap\n  root((Error generating mindmap))';
    }
  };

  // Render the mindmap
  useEffect(() => {
    const renderMindmap = async () => {
      if (!containerRef.current || !mindmapData) return;
      
      // Wait for mermaid to be loaded
      if (!mermaid) {
        const mermaidModule = await import('mermaid');
        mermaid = mermaidModule.default;
        mermaid.initialize({
          startOnLoad: true,
          theme: 'default',
          securityLevel: 'loose',
          fontFamily: 'Inter, system-ui, sans-serif',
          mindmap: {
            padding: 20,
            maxNodeSizeRatio: 0.9,
          }
        });
      }
      
      setIsLoading(true);
      setError(null);
      
      try {
        const mermaidSyntax = generateMermaidSyntax(mindmapData);
        const elementId = `mindmap-${Date.now()}`;
        
        // Clear previous content
        containerRef.current.innerHTML = '';
        
        // Create a div for the mindmap
        const mindmapDiv = document.createElement('div');
        mindmapDiv.id = elementId;
        mindmapDiv.style.transform = `scale(${zoom})`;
        mindmapDiv.style.transformOrigin = 'top left';
        containerRef.current.appendChild(mindmapDiv);
        
        // Render with Mermaid
        const { svg } = await mermaid.render(elementId, mermaidSyntax);
        mindmapDiv.innerHTML = svg;
        
      } catch (err) {
        console.error('Error rendering mindmap:', err);
        setError('Failed to render mindmap. The data might be malformed.');
      } finally {
        setIsLoading(false);
      }
    };

    renderMindmap();
  }, [mindmapData, zoom]);

  const handleDownload = () => {
    if (!containerRef.current) return;
    
    const svgElement = containerRef.current.querySelector('svg');
    if (!svgElement) return;
    
    // Create a blob from the SVG
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    
    // Create download link
    const url = URL.createObjectURL(svgBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mindmap.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleRefresh = () => {
    setZoom(1);
    // Trigger re-render by updating a state
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 100);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.4));
  };

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gray-50 flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-900">Mindmap Visualization</h4>
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomOut}
            disabled={zoom <= 0.4}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-xs text-gray-500 min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomIn}
            disabled={zoom >= 2}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDownload}
          >
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-sm text-gray-600">Generating mindmap...</span>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <div className="text-red-600 text-sm mb-2">{error}</div>
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              Try Again
            </Button>
          </div>
        ) : (
          <div className="overflow-auto max-h-96">
            <div ref={containerRef} className="min-h-[200px]" />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t bg-gray-50">
        <p className="text-xs text-gray-500">
          Mindmap shows key concepts and relationships from the AI response
        </p>
      </div>
    </div>
  );
};