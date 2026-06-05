import { useState, useEffect, useCallback } from 'react';
import { documentService } from '../services/api';
import toast from 'react-hot-toast';

export const useDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    try {
      const docs = await documentService.list();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to list documents:', error);
      toast.error('Failed to load documents.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const uploadDocument = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are currently supported.');
      return;
    }

    const tempId = Math.random().toString(36).substring(7);
    setUploadProgress((prev) => ({ ...prev, [tempId]: 0 }));

    try {
      await documentService.upload(file, (percent) => {
        setUploadProgress((prev) => ({ ...prev, [tempId]: percent }));
      });
      toast.success('Document uploaded and processed successfully.');
      await fetchDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
      const detail = error.response?.data?.detail || 'Upload failed. Please try again.';
      toast.error(detail);
    } finally {
      setUploadProgress((prev) => {
        const next = { ...prev };
        delete next[tempId];
        return next;
      });
    }
  };

  const deleteDocument = async (docId) => {
    try {
      await documentService.delete(docId);
      toast.success('Document deleted successfully.');
      setDocuments((prev) => prev.filter((d) => d.doc_id !== docId));
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete document.');
    }
  };

  return {
    documents,
    isLoading,
    uploadProgress,
    refresh: fetchDocuments,
    uploadDocument,
    deleteDocument,
  };
};
