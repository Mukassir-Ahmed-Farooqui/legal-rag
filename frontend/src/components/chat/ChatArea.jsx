import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { ThinkingIndicator } from './ThinkingIndicator';
import { MessageSquare } from 'lucide-react';

const SUGGESTIONS = [
  "Compare termination provisions",
  "Summarize payment obligations",
  "Who owns the intellectual property?",
  "What limitations exist under this agreement?"
];

export const ChatArea = ({ messages, isQuerying, documents = [], onSuggestionClick }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isQuerying]);

  // Scenario 1: No documents uploaded yet
  if (documents.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50/20 text-center select-none">
        <div className="max-w-md space-y-5">
          <div className="h-12 w-12 rounded-full bg-slate-100 border border-slate-200 text-slate-400 flex items-center justify-center mx-auto shadow-xs">
            <MessageSquare className="h-6 w-6" />
          </div>
          
          <div className="space-y-2">
            <h2 className="text-xl font-extrabold text-slate-800 tracking-tight">
              ClauseScope Workspace
            </h2>
            <p className="text-xs text-slate-550 leading-relaxed max-w-xs mx-auto">
              No agreements uploaded yet. Drag & drop or browse in the left repository panel to import contracts (NDAs, Vendor Contracts, Service agreements, etc.) and begin analysis.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Scenario 2: Documents exist, but no query has been submitted yet
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50/20 text-center select-none">
        <div className="max-w-md space-y-6">
          <div className="h-12 w-12 rounded-full bg-blue-50 text-blue-650 border border-blue-100 flex items-center justify-center mx-auto shadow-md animate-pulse">
            <MessageSquare className="h-6 w-6" />
          </div>
          
          <div className="space-y-2">
            <h2 className="text-xl font-extrabold text-slate-800 tracking-tight">
              ClauseScope Workspace
            </h2>
            <p className="text-xs text-slate-550 leading-relaxed max-w-xs mx-auto">
              ClauseScope is ready. Ask natural language questions about your active agreements, inspect source context, and retrieve secure citation-grounded analysis.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">
              Suggested Audits
            </span>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => onSuggestionClick && onSuggestionClick(s)}
                  className="px-3.5 py-2 bg-white hover:bg-blue-50/40 border border-slate-200 hover:border-blue-300 text-slate-700 hover:text-blue-700 text-xs font-bold rounded-xl shadow-xs transition-all cursor-pointer"
                >
                  💡 {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Scenario 3: Chat log history exists
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0 bg-slate-50/20 select-text">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
      ))}
      {isQuerying && <ThinkingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatArea;
