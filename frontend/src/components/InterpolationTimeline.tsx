import { Card } from './ui/card';
import { Key, Circle } from 'lucide-react';

interface InterpolationTimelineProps {
  frames?: string[];
  currentFrameIndex?: number;
  onFrameClick?: (index: number) => void;
}

export function InterpolationTimeline({
  frames,
  currentFrameIndex = 0,
  onFrameClick
}: InterpolationTimelineProps) {
  const hasFrames = frames && frames.length > 0;
  const totalFrames = hasFrames ? frames.length : 10;

  // Assume first and last frames are keyframes
  const keyframeIndices = hasFrames ? [0, frames.length - 1] : [0, 9];

  return (
    <Card className="bg-white border border-zinc-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-zinc-900">Timeline</h3>
          <span className="text-xs text-zinc-500">{totalFrames} frames total</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-zinc-600">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-amber-200 rounded-sm" />
            <span>Keyframe</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-blue-100 rounded-sm border border-blue-200" />
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
                const isCurrent = index === currentFrameIndex;

                return (
                  <div
                    key={index}
                    className="flex flex-col items-center gap-2 group cursor-pointer"
                    onClick={() => onFrameClick?.(index)}
                  >
                    {/* Frame Box */}
                    <div
                      className={`w-12 h-12 rounded-lg border-2 flex items-center justify-center transition-all ${
                        isCurrent
                          ? 'bg-purple-200 border-purple-400 ring-2 ring-purple-300'
                          : isKeyframe
                          ? 'bg-amber-200 border-amber-200 hover:bg-amber-300'
                          : 'bg-blue-50 border-blue-200 hover:border-purple-200'
                      }`}
                    >
                      {isKeyframe ? (
                        <Key className="h-5 w-5 text-amber-700" />
                      ) : (
                        <Circle className={`h-3 w-3 ${isCurrent ? 'text-purple-600' : 'text-blue-300'}`} />
                      )}
                    </div>

                    {/* Frame Number */}
                    <span
                      className={`text-xs font-medium ${
                        isCurrent
                          ? 'text-purple-600'
                          : isKeyframe
                          ? 'text-amber-600'
                          : 'text-zinc-400'
                      }`}
                    >
                      {index + 1}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Frame Info */}
      {hasFrames && (
        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-zinc-500">
          <span>
            Current: Frame {currentFrameIndex + 1}
            {keyframeIndices.includes(currentFrameIndex) ? ' (Keyframe)' : ' (Interpolated)'}
          </span>
        </div>
      )}
    </Card>
  );
}
