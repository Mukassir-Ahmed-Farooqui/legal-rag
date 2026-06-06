import React, { useState, useRef } from 'react';
import { Upload, Loader } from 'lucide-react';
import { truncateFilename } from '../../services/api';
import toast from 'react-hot-toast';

export const UploadZone = ({ onUpload, progress }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndUpload(e.target.files[0]);
    }
  };

  const validateAndUpload = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are currently supported by the backend.');
      return;
    }
    onUpload(file);
  };

  const triggerFilePicker = () => {
    fileInputRef.current?.click();
  };

  const activeUploads = Object.entries(progress);

  return (
    <div className="space-y-4">
      {/* Upload Drag/Drop Card */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFilePicker}
        className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all flex flex-col items-center justify-center ${
          isDragActive
            ? 'border-blue-600 bg-blue-50/25'
            : 'border-slate-200 hover:border-blue-300 bg-slate-50/50 hover:bg-slate-50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        
        <div className="h-9 w-9 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mb-2 shadow-sm border border-slate-200">
          <Upload className="h-4.5 w-4.5" />
        </div>
        
        <p className="text-xs font-bold text-slate-700">
          Upload Documents
        </p>
        <p className="text-[10px] text-slate-400 mt-1 leading-normal">
          Drag & drop PDF or <span className="text-blue-650 font-bold hover:underline">browse files</span> (Max 25MB)
        </p>
      </div>

      {/* Recommended list */}
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 select-none">
        <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-widest block">
          Recommended Formats
        </span>
        <ul className="grid grid-cols-2 gap-1.5 text-[10px] text-slate-600 font-bold">
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            Contracts
          </li>
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            Research Papers
          </li>
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            Technical Documentation
          </li>
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            Reports
          </li>
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            Policies
          </li>
          <li className="flex items-center gap-1">
            <span className="h-1 w-1 bg-blue-500 rounded-full" />
            PDF Documents
          </li>
        </ul>
        <p className="text-[9px] text-slate-450 leading-normal font-semibold border-t border-slate-200 pt-1.5 mt-1">
          Other PDFs are supported. OpenDoc works best with text-based documents.
        </p>
      </div>

      {activeUploads.length > 0 && (
        <div className="space-y-2 border-t border-slate-100 pt-3">
          {activeUploads.map(([name, percent]) => {
            const displayUploadName = truncateFilename(name, 28);
            return (
              <div key={name} className="bg-slate-50 rounded-lg p-2.5 border border-slate-200 flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-[11px] font-semibold text-slate-650">
                  <span className="flex items-center gap-1.5 truncate pr-4 max-w-[200px]" title={name}>
                    <Loader className="h-3 w-3 animate-spin text-blue-650 shrink-0" />
                    <span className="truncate">{displayUploadName}</span>
                  </span>
                  <span className="shrink-0">{percent === 90 ? 'Processing...' : `${percent}%`}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-blue-650 h-full rounded-full transition-all duration-300"
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default UploadZone;
