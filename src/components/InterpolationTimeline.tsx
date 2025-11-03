import { Card } from './ui/card';
import { Key, Circle } from 'lucide-react';

// Mock data: 2 keyframes with 8 intermediate frames
const totalFrames = 10;
const keyframeIndices = [0, 9]; // First and last frames are keyframes

export function InterpolationTimeline() {
  return (
    <Card className="bg-white border border-zinc-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm text-zinc-900">Timeline</h3>
          <span className="text-xs text-zinc-500">10 frames total</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-zinc-600">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-purple-300 rounded-sm" />
            <span>Keyframe</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-purple-100 rounded-sm border border-purple-200" />
            <span>Interpolated</span>
          </div>
        </div>
      </div>
      
      {/* Timeline Track */}
      <div className="relative">
        {/* Background Track */}
        <div className="h-20 bg-zinc-50 rounded-lg border border-zinc-200 relative overflow-hidden">
          <div className="absolute inset-0 flex items-center px-4">
            <div className="flex-1 flex justify-between items-center">
              {Array.from({ length: totalFrames }).map((_, index) => {
                const isKeyframe = keyframeIndices.includes(index);
                
                return (
                  <div key={index} className="flex flex-col items-center gap-2 group cursor-pointer">
                    {/* Frame Box */}
                    <div
                      className={`w-12 h-12 rounded-lg border-2 flex items-center justify-center transition-all ${
                        isKeyframe
                          ? 'bg-purple-300 border-purple-300 hover:bg-purple-400'
                          : 'bg-purple-50 border-purple-200 hover:border-purple-300'
                      }`}
                    >
                      {isKeyframe ? (
                        <Key className="h-5 w-5 text-purple-800" />
                      ) : (
                        <Circle className="h-3 w-3 text-purple-300" />
                      )}
                    </div>
                    
                    {/* Frame Number */}
                    <span className={`text-xs ${isKeyframe ? 'text-purple-700' : 'text-zinc-400'}`}>
                      {index + 1}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        
        {/* Playhead indicator */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-0.5 h-20 bg-purple-400 pointer-events-none">
          <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-3 h-3 bg-purple-400 rounded-full shadow-lg" />
        </div>
      </div>
      
      {/* Frame Info */}
      <div className="mt-4 flex items-center justify-center gap-2 text-xs text-zinc-500">
        <span>Current: Frame 5 (Interpolated)</span>
      </div>
    </Card>
  );
}
