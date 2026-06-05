import React from 'react';

export const CitationChip = ({ number, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center mx-0.5 px-1 bg-blue-650 hover:bg-blue-700 text-white rounded text-[10px] font-bold font-mono h-4 min-w-4 hover:scale-105 transition-all select-none cursor-pointer align-middle"
      title={`View Citation #${number}`}
    >
      {number}
    </button>
  );
};

export default CitationChip;
