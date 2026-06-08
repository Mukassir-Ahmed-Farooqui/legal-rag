import React, { useState } from 'react';
import { Shield, Copy, Check, FileText, Sparkles, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { CitationChip } from './CitationChip';
import { truncateFilename } from '../../services/api';
import toast from 'react-hot-toast';

export const MessageBubble = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(null);
  const [showAllCitations, setShowAllCitations] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    toast.success('Answer copied successfully');
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (date) => {
    try {
      const d = new Date(date);
      return d.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  const handleCitationClick = (citationIndex) => {
    if (citationIndex >= 3 && !showAllCitations) {
      setShowAllCitations(true);
      setTimeout(() => {
        setHighlightedIndex(citationIndex);
        const cardEl = document.getElementById(`cit-${message.id}-${citationIndex}`);
        if (cardEl) {
          cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        setTimeout(() => {
          setHighlightedIndex((current) => current === citationIndex ? null : current);
        }, 3000);
      }, 100);
      return;
    }

    setHighlightedIndex(citationIndex);
    // Auto clear highlight after 3 seconds
    setTimeout(() => {
      setHighlightedIndex((current) => current === citationIndex ? null : current);
    }, 3000);

    // Scroll citation card into view if needed
    const cardEl = document.getElementById(`cit-${message.id}-${citationIndex}`);
    if (cardEl) {
      cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  // Helper to parse citations [1], [2] inside text node strings
  const renderTextWithCitations = (text, onCitationClick) => {
    if (typeof text !== 'string') return text;
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      const isCitation = /^\[\d+\]$/.test(part);
      if (isCitation) {
        const citationNumber = parseInt(part.slice(1, -1), 10);
        const citationIndex = citationNumber - 1;
        return (
          <CitationChip
            key={index}
            number={citationNumber}
            onClick={() => onCitationClick(citationIndex)}
          />
        );
      }
      return part;
    });
  };

  // Helper to recursively map React children and inject citation chips into text leaves
  const processChildren = (children) => {
    return React.Children.map(children, (child) => {
      if (typeof child === 'string') {
        return renderTextWithCitations(child, handleCitationClick);
      }
      if (React.isValidElement(child)) {
        if (child.props && child.props.children) {
          return React.cloneElement(child, {
            ...child.props,
            children: processChildren(child.props.children),
          });
        }
      }
      return child;
    });
  };

  // Custom render components for ReactMarkdown
  const markdownComponents = {
    p: ({ children }) => <p className="mb-2.5 last:mb-0 text-slate-800 leading-relaxed font-sans">{processChildren(children)}</p>,
    li: ({ children }) => <li className="list-disc ml-5 mb-1.5 text-slate-800 leading-normal font-sans">{processChildren(children)}</li>,
    ol: ({ children }) => <ol className="list-decimal ml-5 mb-3 space-y-1 font-sans">{processChildren(children)}</ol>,
    ul: ({ children }) => <ul className="list-disc ml-5 mb-3 space-y-1 font-sans">{processChildren(children)}</ul>,
    h1: ({ children }) => <h1 className="text-base font-extrabold text-slate-900 mt-4 mb-2 font-sans tracking-tight">{processChildren(children)}</h1>,
    h2: ({ children }) => <h2 className="text-sm font-extrabold text-slate-800 mt-3.5 mb-2 font-sans tracking-tight">{processChildren(children)}</h2>,
    h3: ({ children }) => <h3 className="text-xs font-extrabold text-slate-850 mt-3 mb-1.5 font-sans tracking-tight">{processChildren(children)}</h3>,
    strong: ({ children }) => <strong className="font-extrabold text-slate-900 font-sans">{processChildren(children)}</strong>,
    em: ({ children }) => <em className="italic text-slate-850 font-sans">{processChildren(children)}</em>,
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-slate-200 pl-3 italic text-slate-650 my-2 bg-slate-50/50 py-1 pr-2 rounded-r font-sans">
        {processChildren(children)}
      </blockquote>
    ),
  };

  if (isUser) {
    return (
      <div className="flex justify-end w-full select-text">
        <div className="max-w-[75%] bg-blue-750 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm shadow-sm text-xs md:text-sm leading-relaxed border border-blue-800">
          <p className="whitespace-pre-wrap font-sans font-medium">{message.content}</p>
          <span className="text-[10px] text-blue-200 block text-right mt-1.5 font-medium select-none">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    );
  }

  const citations = message.citations || [];
  const citationCount = citations.length;
  const isError = message.isError === true;
  const displayedCitations = showAllCitations ? citations : citations.slice(0, 3);

  // Build metadata string: latency + sources count
  const latencyPart = message.latencyMs !== undefined 
    ? `${(message.latencyMs / 1000).toFixed(1)}s` 
    : '';
  const sourcesPart = citationCount > 0 
    ? `${citationCount} Evidence Chunk${citationCount !== 1 ? 's' : ''}` 
    : '';
  const modelPart = message.model ? message.model : '';
  const metadataString = [modelPart, latencyPart, sourcesPart].filter(Boolean).join(' • ');

  return (
    <div className="flex justify-start w-full gap-3 select-text">
      {/* Bot Avatar */}
      <div className="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center border border-slate-700 shrink-0 select-none shadow-sm mt-1">
        <Shield className="h-4.5 w-4.5" />
      </div>

      <div className="max-w-[80%] space-y-2.5 flex-1 min-w-0">
        {/* Header row */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 select-none">
          <span className="text-slate-800 font-bold">OpenDoc</span>
          <span>•</span>
          <span>{formatTime(message.timestamp)}</span>
        </div>

        {/* Content Container (Professional Answer Card) */}
        {isError ? (
          /* Error Answer Card */
          <div className="bg-red-50/20 border border-red-200 rounded-2xl shadow-sm overflow-hidden w-full transition-all">
            <div className="bg-red-55/10 px-4 py-3 border-b border-red-100 flex items-center justify-between select-none">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <span className="text-xs font-extrabold text-red-800 uppercase tracking-wider">Analysis Failed</span>
              </div>
            </div>
            <div className="p-4 text-xs md:text-sm text-red-800 leading-relaxed font-sans font-bold">
              {message.content}
            </div>
          </div>
        ) : (
          /* Successful Answer Card */
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden w-full transition-all hover:border-slate-300 min-w-0">
            <div className="bg-slate-50/80 px-4 py-2.5 border-b border-slate-150 flex items-center justify-between select-none">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-650" />
                <span className="text-xs font-extrabold text-slate-800 uppercase tracking-wider">Generated Analysis</span>
              </div>
              
              <div className="flex items-center gap-3">
                {metadataString && (
                  <span className="text-[10px] text-slate-500 font-bold font-mono">
                    {metadataString}
                  </span>
                )}
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[10px] font-bold text-blue-650 hover:text-blue-700 bg-white border border-slate-200 hover:border-slate-350 px-2 py-1 rounded-md shadow-sm transition-all cursor-pointer"
                  title="Copy analysis answer to clipboard"
                >
                  {copied ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-600" />
                      <span className="text-emerald-600">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>📋 Copy Answer</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="p-4 text-xs md:text-sm leading-relaxed text-slate-800 bg-white select-text overflow-hidden break-words">
              <ReactMarkdown components={markdownComponents}>
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Redesigned Citations Block */}
            {citationCount > 0 && (
              <div className="bg-slate-50/40 p-4 border-t border-slate-150 space-y-3">
                <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wider block select-none">
                  Evidence ({citationCount})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {displayedCitations.map((cit, idx) => {
                    const isHighlighted = highlightedIndex === idx;
                    const truncatedName = truncateFilename(cit.document, 28);
                    
                    // Prioritize section name, document name, and page number hierarchy
                    const displaySection = cit.section && cit.section.trim() !== '' 
                      ? cit.section 
                      : 'Section Unspecified';

                    return (
                      <div
                        key={idx}
                        id={`cit-${message.id}-${idx}`}
                        className={`p-3 rounded-xl border transition-all text-left flex flex-col justify-between ${
                          isHighlighted
                            ? 'border-blue-500 bg-blue-50/60 ring-1 ring-blue-400 scale-[1.01] shadow-sm'
                            : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-xs'
                        }`}
                      >
                        <div className="space-y-1 min-w-0">
                          {/* Primary: Section Name */}
                          <div className="flex items-start gap-2">
                            <span className="h-4.5 w-4.5 rounded bg-slate-100 text-slate-650 border border-slate-200 flex items-center justify-center text-[9px] font-bold font-mono shrink-0 select-none">
                              {idx + 1}
                            </span>
                            <span className="text-[11px] font-bold text-slate-900 leading-snug break-words block flex-1">
                              {displaySection}
                            </span>
                          </div>

                          {/* Secondary & Tertiary metadata */}
                          <div className="pl-6.5 space-y-0.5">
                            <div className="flex items-center gap-1 text-[10px] text-slate-500 font-semibold truncate" title={cit.document}>
                              <FileText className="h-3 w-3 text-slate-400 shrink-0" />
                              <span className="truncate">{truncatedName}</span>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              {/* Page Number (Tertiary) */}
                              <span className="text-[9px] text-slate-400 font-bold font-mono block">
                                Page {cit.page !== undefined ? cit.page : 'N/A'}
                              </span>
                              
                              {/* Score */}
                              {cit.score !== undefined && (
                                <span className="text-[9px] text-slate-400 font-bold font-mono block">
                                  • Score: {cit.score.toFixed(4)}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Evidence snippet if available */}
                        {(cit.preview || cit.snippet || cit.text) && (
                          <blockquote className="mt-2.5 text-[10px] leading-relaxed text-slate-500 font-medium border-l-2 border-slate-300 pl-2.5 italic line-clamp-3 select-text bg-slate-50/80 p-1.5 rounded" title={cit.chunk_id}>
                            "{cit.preview || cit.snippet || cit.text}"
                          </blockquote>
                        )}
                      </div>
                    );
                  })}
                </div>
                {citationCount > 3 && (
                  <button
                    onClick={() => setShowAllCitations(!showAllCitations)}
                    className="mt-3 text-[10px] font-bold text-blue-600 hover:text-blue-700 w-full text-center py-1.5 bg-blue-50/50 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                  >
                    {showAllCitations ? 'Show Less Evidence' : `Show ${citationCount - 3} More Evidence Chunks`}
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
