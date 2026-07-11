'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { documentsApi } from '@/lib/api';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { formatFileSize } from '@/lib/utils';

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(0);
    setUploadStatus({ type: null, message: '' });

    try {
      await documentsApi.upload(
        file,
        title || file.name,
        (progress) => setUploadProgress(progress)
      );
      setUploadStatus({
        type: 'success',
        message: `Successfully uploaded ${file.name}`
      });
      setTitle('');
      onUploadSuccess();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.message ||
                          'Upload failed due to an unexpected error';
      setUploadStatus({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [title, onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/x-pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc', '.docx'],
      'application/vnd.ms-word': ['.doc', '.docx'],
      'text/plain': ['.txt'],
      'text/txt': ['.txt'],
      'application/vnd.ms-excel': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    disabled: uploading,
    validator: (file) => {
      // Additional client-side validation
      if (file.size === 0) {
        return {
          code: 'file-empty',
          message: 'File is empty'
        };
      }
      if (!file.name || file.name.trim().length === 0) {
        return {
          code: 'invalid-name',
          message: 'File name is invalid'
        };
      }
      return null;
    }
  });

  // Show rejection errors
  React.useEffect(() => {
    if (fileRejections.length > 0) {
      const rejection = fileRejections[0];
      const errors = rejection.errors.map(e => e.message).join(', ');
      setUploadStatus({
        type: 'error',
        message: `File rejected: ${errors}`
      });
    }
  }, [fileRejections]);

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Upload Document</h2>
      
      <div className="space-y-4">
        <Input
          label="Document Title (Optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter a custom title for the document"
          disabled={uploading}
        />

        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            <div className={`p-3 rounded-full ${isDragActive ? 'bg-blue-100' : 'bg-gray-100'}`}>
              <Upload className={`h-8 w-8 ${isDragActive ? 'text-blue-600' : 'text-gray-600'}`} />
            </div>
            
            {uploading ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Uploading... {uploadProgress}%</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop a document'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or <span className="text-blue-600 font-medium">browse files</span>
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Supports PDF, DOCX, TXT, XLSX, CSV (max 50MB)
                </p>
              </div>
            )}
          </div>
        </div>

        {acceptedFiles.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Selected File:</h4>
            {acceptedFiles.map((file) => (
              <div key={file.name} className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-gray-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {uploadStatus.type && (
          <div className={`
            flex items-start space-x-2 p-3 rounded-lg
            ${uploadStatus.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
            }
          `}>
            {uploadStatus.type === 'success' ? (
              <CheckCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p className="text-sm font-medium">{uploadStatus.message}</p>
              {uploadStatus.type === 'error' && (
                <p className="text-xs mt-1 opacity-75">
                  Please check your file and try again. If the problem persists, contact support.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};