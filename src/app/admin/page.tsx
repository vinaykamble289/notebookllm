'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DocumentUpload } from '@/components/admin/DocumentUpload';
import { DocumentList } from '@/components/admin/DocumentList';
import { documentsApi, DocumentMetadata } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { ShieldAlert } from 'lucide-react';

export default function AdminPage() {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated, isAdmin, isLoading } = useAuth();
  const router = useRouter();

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    } else if (!isLoading && !isAdmin) {
      // User is authenticated but not admin - show access denied
    }
  }, [isLoading, isAuthenticated, isAdmin, router]);

  const fetchDocuments = async () => {
    try {
      const response = await documentsApi.list();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchDocuments();
    }
  }, [isAdmin]);

  const handleUploadSuccess = () => {
    fetchDocuments();
  };

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Show access denied for non-admin users
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ShieldAlert className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">
            You do not have permission to access this page.
            <br />
            Only administrators can access the admin dashboard.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Upload and manage documents for the AI Academic Assistant
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          </div>
          
          <div className="lg:col-span-2">
            <DocumentList 
              documents={documents} 
              loading={loading}
              onRefresh={fetchDocuments}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
