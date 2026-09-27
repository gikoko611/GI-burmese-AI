import React from 'react';
import { Film, Wrench, Lightbulb, Cpu, GraduationCap, HelpCircle } from 'lucide-react';
import { ContentType } from '../types';

interface ContentTypeSelectorProps {
  selected: ContentType;
  onSelect: (type: ContentType) => void;
}

interface OptionConfig {
  type: ContentType;
  label: string;
  burmeseLabel: string;
  description: string;
  icon: React.ReactNode;
}

const contentTypes: OptionConfig[] = [
  {
    type: 'Movie Recap',
    label: 'Movie Recap',
    burmeseLabel: 'ရုပ်ရှင်ဇာတ်လမ်း အကျဉ်းချုပ်',
    description: 'Cinematic plot summaries & twists',
    icon: <Film className="w-4 h-4" />
  },
  {
    type: 'Tutorial / How-to',
    label: 'Tutorial / How-to',
    burmeseLabel: 'အဆင့်ဆင့် သင်ခန်းစာ',
    description: 'Clear step-by-step practical guides',
    icon: <Wrench className="w-4 h-4" />
  },
  {
    type: 'Tips & Tricks',
    label: 'Tips & Tricks',
    burmeseLabel: 'နည်းလမ်းတိုများနှင့် အကြံပြုချက်',
    description: 'Actionable productivity insights',
    icon: <Lightbulb className="w-4 h-4" />
  },
  {
    type: 'Technology',
    label: 'Technology',
    burmeseLabel: 'နည်းပညာနှင့် AI ဆန်းသစ်မှု',
    description: 'Software, hardware & digital trends',
    icon: <Cpu className="w-4 h-4" />
  },
  {
    type: 'Educational',
    label: 'Educational',
    burmeseLabel: 'ပညာရေးနှင့် ဗဟုသုတ',
    description: 'Academic concepts & scientific depth',
    icon: <GraduationCap className="w-4 h-4" />
  },
  {
    type: 'General Explanation',
    label: 'General Explanation',
    burmeseLabel: 'ယေဘုယျ ရှင်းလင်းချက်',
    description: 'Everyday topics simplified for all',
    icon: <HelpCircle className="w-4 h-4" />
  }
];

export const ContentTypeSelector: React.FC<ContentTypeSelectorProps> = ({
  selected,
  onSelect
}) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-zinc-200">
          Content Type
        </label>
        <span className="text-xs text-zinc-500">Target narrative format</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {contentTypes.map((item) => {
          const isSelected = selected === item.type;
          return (
            <button
              key={item.type}
              type="button"
              onClick={() => onSelect(item.type)}
              className={`text-left p-3 rounded-xl border transition-all duration-150 relative cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'bg-amber-500/10 border-amber-500/80 ring-1 ring-amber-500/20 text-zinc-100 shadow-sm'
                  : 'bg-zinc-900/80 border-zinc-800/90 text-zinc-300 hover:border-zinc-700 hover:bg-zinc-800/60'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-2">
                <div
                  className={`p-1.5 rounded-lg ${
                    isSelected
                      ? 'bg-amber-500 text-zinc-950 font-bold'
                      : 'bg-zinc-800 text-zinc-400'
                  }`}
                >
                  {item.icon}
                </div>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-amber-400 shadow-sm animate-pulse"></span>
                )}
              </div>

              <div>
                <div className="font-semibold text-xs sm:text-sm tracking-tight text-zinc-100">
                  {item.label}
                </div>
                <div className="text-[11px] font-burmese text-amber-300/80 mt-0.5 line-clamp-1">
                  {item.burmeseLabel}
                </div>
                <div className="text-[11px] text-zinc-500 mt-1 line-clamp-1">
                  {item.description}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
