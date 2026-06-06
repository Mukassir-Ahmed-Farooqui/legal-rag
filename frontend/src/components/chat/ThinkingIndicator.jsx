import React, { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';

const LOADING_STEPS = [
  "Searching documents...",
  "Retrieving context...",
  "Synthesizing response..."
];

export const ThinkingIndicator = () => {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIndex((prevIndex) => {
        // Keep repeating the last step once reached, or cycle.
        // Let's cycle or stay on the final step "Synthesizing response..." which fits long queries
        if (prevIndex < LOADING_STEPS.length - 1) {
          return prevIndex + 1;
        }
        return prevIndex; // Remain on "Synthesizing response..."
      });
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex justify-start w-full gap-3 select-none animate-pulse">
      {/* Bot Avatar */}
      <div className="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center border border-slate-700 shrink-0 shadow-sm mt-1">
        <Shield className="h-4.5 w-4.5" />
      </div>

      <div className="max-w-[75%] space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-550">
          <span className="text-slate-800 font-bold">OpenDoc Pipeline</span>
          <span>•</span>
          <span className="text-blue-650 font-bold transition-all duration-500 ease-in-out">
            {LOADING_STEPS[stepIndex]}
          </span>
        </div>

        <div className="bg-white border border-slate-200 text-slate-800 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-1.5 w-fit">
          <div className="h-2 w-2 rounded-full bg-blue-650 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="h-2 w-2 rounded-full bg-blue-650 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="h-2 w-2 rounded-full bg-blue-650 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};

export default ThinkingIndicator;
