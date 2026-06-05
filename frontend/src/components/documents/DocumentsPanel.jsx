import React from 'react';
import { UploadZone } from './UploadZone';
import { DocumentCard } from './DocumentCard';
import { HelpCircle } from 'lucide-react';

export const DocumentsPanel = ({
  documents,
  uploadProgress,
  onUpload,
  onDeleteDoc,
}) => {
  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <UploadZone onUpload={onUpload} progress={uploadProgress} />

      {/* Document Cards List */}
      <div className="space-y-2.5">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
          Contracts list ({documents.length})
        </h4>

        {documents.length === 0 ? (
          <div className="bg-slate-50/50 rounded-xl border border-slate-200 p-6 text-center text-slate-400">
            <HelpCircle className="h-7 w-7 mx-auto text-slate-300 mb-2" />
            <p className="text-xs font-semibold">No contracts active</p>
            <p className="text-[10px] text-slate-400 mt-1 leading-normal max-w-[200px] mx-auto">
              Choose a PDF file to begin extracting context segments.
            </p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.doc_id}
                document={doc}
                onDelete={() => onDeleteDoc(doc.doc_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsPanel;
