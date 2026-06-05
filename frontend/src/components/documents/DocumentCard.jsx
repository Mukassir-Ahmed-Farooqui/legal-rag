import React from 'react';
import { FileText, Trash2 } from 'lucide-react';
import { truncateFilename } from '../../services/api';

export const DocumentCard = ({ document, onDelete }) => {
  const handleDeleteClick = (e) => {
    e.stopPropagation();
    const confirm = window.confirm(`Are you sure you want to delete "${document.filename}"? This will permanently delete the agreement and its vector embeddings.`);
    if (confirm) {
      onDelete();
    }
  };

  const truncatedName = truncateFilename(document.filename, 28);

  return (
    <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between gap-3 hover:border-slate-350 hover:shadow-xs transition-all select-none">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shrink-0">
          <FileText className="h-4.5 w-4.5" />
        </div>
        <div className="min-w-0 flex-1">
          <p 
            className="text-xs font-bold text-slate-800 truncate" 
            title={document.filename}
          >
            {truncatedName}
          </p>
          <p className="text-[9px] text-slate-400 font-mono truncate" title={document.doc_id}>
            ID: {document.doc_id}
          </p>
        </div>
      </div>

      <button
        onClick={handleDeleteClick}
        className="p-1.5 border border-slate-200 hover:border-red-200 text-slate-400 hover:text-red-500 hover:bg-red-50/55 rounded-lg cursor-pointer transition-all shrink-0 bg-white shadow-xs"
        title="Delete contract"
      >
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </div>
  );
};

export default DocumentCard;
