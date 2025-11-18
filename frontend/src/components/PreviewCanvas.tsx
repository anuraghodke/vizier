import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Image as ImageIcon, Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import { Slider } from './ui/slider';
import { getFrameUrl } from '../utils/api';

interface PreviewCanvasProps {
  jobId?: string;
  frames?: string[];
}

export function PreviewCanvas({ jobId, frames }: PreviewCanvasProps) {
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [fps, setFps] = useState(12);

  const hasFrames = frames && frames.length > 0;
  const currentFrame = hasFrames && jobId ? frames[currentFrameIndex] : null;
  const currentFrameUrl = currentFrame ? getFrameUrl(jobId!, currentFrame) : null;

  // Auto-play functionality
  useEffect(() => {
    if (!isPlaying || !hasFrames) return;

    const interval = setInterval(() => {
      setCurrentFrameIndex((prev) => (prev + 1) % frames.length);
    }, 1000 / fps);

    return () => clearInterval(interval);
  }, [isPlaying, hasFrames, frames, fps]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handlePrevFrame = () => {
    if (!hasFrames) return;
    setCurrentFrameIndex((prev) => (prev - 1 + frames.length) % frames.length);
    setIsPlaying(false);
  };

  const handleNextFrame = () => {
    if (!hasFrames) return;
    setCurrentFrameIndex((prev) => (prev + 1) % frames.length);
    setIsPlaying(false);
  };

  const handleFrameChange = (value: number[]) => {
    setCurrentFrameIndex(value[0]);
    setIsPlaying(false);
  };

  if (!hasFrames) {
    return (
      <Card className="flex-1 bg-white border border-zinc-200 flex items-center justify-center min-h-[300px]">
        <div className="text-center">
          <div className="w-16 h-16 rounded-lg bg-zinc-100 flex items-center justify-center mx-auto mb-3">
            <ImageIcon className="h-8 w-8 text-zinc-400" />
          </div>
          <p className="text-sm text-zinc-500">Preview will appear here</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex-1 bg-white border border-zinc-200 flex flex-col min-h-[300px]">
      {/* Canvas Area */}
      <div className="flex-1 flex items-center justify-center p-6 bg-zinc-50">
        {currentFrameUrl && (
          <img
            src={currentFrameUrl}
            alt={`Frame ${currentFrameIndex + 1}`}
            className="max-w-full max-h-full object-contain"
          />
        )}
      </div>

      {/* Controls */}
      <div className="p-4 border-t border-zinc-200 space-y-3">
        {/* Frame Scrubber */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-zinc-500">
            <span>Frame {currentFrameIndex + 1} / {frames.length}</span>
            <span>{fps} FPS</span>
          </div>
          <Slider
            value={[currentFrameIndex]}
            min={0}
            max={frames.length - 1}
            step={1}
            onValueChange={handleFrameChange}
            className="w-full"
          />
        </div>

        {/* Playback Controls */}
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevFrame}
            disabled={!hasFrames}
          >
            <SkipBack className="h-4 w-4" />
          </Button>

          <Button
            variant="default"
            size="sm"
            onClick={handlePlayPause}
            disabled={!hasFrames}
          >
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleNextFrame}
            disabled={!hasFrames}
          >
            <SkipForward className="h-4 w-4" />
          </Button>

          {/* FPS Control */}
          <div className="flex items-center gap-2 ml-4">
            <span className="text-xs text-zinc-600">FPS:</span>
            <select
              value={fps}
              onChange={(e) => setFps(Number(e.target.value))}
              className="text-xs border border-zinc-300 rounded px-2 py-1"
            >
              <option value={6}>6</option>
              <option value={12}>12</option>
              <option value={24}>24</option>
              <option value={30}>30</option>
            </select>
          </div>
        </div>
      </div>
    </Card>
  );
}
