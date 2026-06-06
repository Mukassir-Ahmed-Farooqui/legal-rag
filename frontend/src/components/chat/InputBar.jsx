import React, { useState, useRef, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

const PLACEHOLDERS = [
  "Ask questions about your documents...",
  "Summarize the selected documents...",
  "What are the key findings in this report?",
  "Compare the selected documents..."
];

export const InputBar = ({
  onSend,
  disabled,
  selectedDocIds = [],
  documents = [],
}) => {
  const [text, setText] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const textareaRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDERS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Auto-grow height up to 4 lines
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const singleLineHeight = 36;
      const maxHeight = singleLineHeight * 4;
      const nextHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = `${nextHeight}px`;
    }
  }, [text]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
      // Reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const isZeroDocs = documents.length === 0;
  const isZeroSelected = selectedDocIds.length === 0 && documents.length > 0;
  const isInputDisabled = disabled || isZeroDocs || isZeroSelected;
  const isButtonDisabled = isInputDisabled || !text.trim();

  let activePlaceholder = PLACEHOLDERS[placeholderIndex];
  if (isZeroDocs) activePlaceholder = "Upload a document to start asking questions";
  else if (isZeroSelected) activePlaceholder = "Select a document to ask questions";

  return (
    <div className="p-4 bg-white border-t border-slate-200 shrink-0">
      {isZeroSelected && (
        <div className="max-w-3xl mx-auto mb-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-xs font-semibold animate-in fade-in slide-in-from-bottom-1">
          <span className="text-sm">⚠</span>
          <span>No documents selected. Select one or more documents from the document library to begin analysis.</span>
        </div>
      )}
      <div className={`max-w-3xl mx-auto flex items-end gap-2.5 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 transition-all ${
        isInputDisabled ? 'opacity-70' : 'focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 focus-within:bg-white'
      }`}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isInputDisabled}
          placeholder={activePlaceholder}
          className="flex-1 resize-none bg-transparent outline-none border-none py-1 text-sm text-slate-800 placeholder-slate-400 max-h-[144px] min-h-[36px] font-sans leading-relaxed disabled:opacity-50"
        />

        <button
          onClick={handleSubmit}
          disabled={isButtonDisabled}
          className="px-4 py-2 text-xs font-bold rounded-lg text-white shadow-sm transition-all cursor-pointer select-none shrink-0 bg-blue-650 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none min-w-[130px] flex items-center justify-center h-9"
          title={isButtonDisabled ? "Write a query first" : "Submit analysis query"}
        >
          {disabled ? (
            <span className="flex items-center gap-1.5 justify-center">
              <Loader2 className="h-3.5 w-3.5 animate-spin shrink-0" />
              <span>Analyzing...</span>
            </span>
          ) : selectedDocIds.length > 0 ? (
            selectedDocIds.length === 1 ? 'Analyze Document' : 'Analyze Selection'
          ) : (
            'Analyze Documents'
          )}
        </button>
      </div>
      <p className="text-[10px] text-slate-400 text-center mt-2 font-medium">
        OpenDoc answers are based strictly on indexed text blocks. Audits are verified via page references.
      </p>
    </div>
  );
};

export default InputBar;
