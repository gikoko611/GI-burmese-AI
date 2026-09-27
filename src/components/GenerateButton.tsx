import React from 'react';
import { Sparkles, Loader2, ArrowRight } from 'lucide-react';

interface GenerateButtonProps {
  onClick: () => void;
  isLoading: boolean;
  loadingStep?: string;
  disabled?: boolean;
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onClick,
  isLoading,
  loadingStep,
  disabled
}) => {
  return (
    <div className="w-full space-y-2">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled || isLoading}
        className="w-full py-4 px-6 rounded-xl font-semibold text-base sm:text-lg transition-all duration-200 cursor-pointer flex items-center justify-center gap-3 relative overflow-hidden group shadow-lg shadow-amber-500/10 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 text-zinc-950 hover:brightness-110 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:brightness-100"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin text-zinc-950" />
            <span>Generating Burmese Content...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5 text-zinc-950 transition-transform group-hover:rotate-12" />
            <span>Generate Burmese Content</span>
            <ArrowRight className="w-4 h-4 text-zinc-950/70 transition-transform group-hover:translate-x-1" />
          </>
        )}
      </button>

      {isLoading && loadingStep && (
        <div className="flex items-center justify-center gap-2 text-xs text-amber-400/90 font-mono tracking-wide animate-pulse">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          <span>{loadingStep}</span>
        </div>
      )}
    </div>
  );
};
