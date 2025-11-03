import { Play, Pause, SkipBack, SkipForward, Volume2, Maximize } from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';

export function VideoCanvas() {
  return (
    <div className="flex-1 bg-zinc-950 flex flex-col">
      {/* Canvas Area */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '16/9', maxWidth: '100%', maxHeight: '100%', width: '90%' }}>
          {/* Video Preview Placeholder */}
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-zinc-800 to-zinc-900">
            <div className="text-center">
              <Play className="h-16 w-16 text-zinc-600 mx-auto mb-2" />
              <p className="text-zinc-500">Preview Canvas</p>
            </div>
          </div>
          
          {/* Canvas Overlay Controls */}
          <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity bg-black/20 flex items-center justify-center">
            <Button size="icon" variant="ghost" className="h-16 w-16 rounded-full bg-white/10 backdrop-blur hover:bg-white/20">
              <Play className="h-8 w-8" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Playback Controls */}
      <div className="h-16 border-t border-zinc-800 flex items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <Button size="icon" variant="ghost" className="text-zinc-400 hover:text-white">
            <SkipBack className="h-4 w-4" />
          </Button>
          <Button size="icon" variant="ghost" className="text-white">
            <Play className="h-5 w-5" />
          </Button>
          <Button size="icon" variant="ghost" className="text-zinc-400 hover:text-white">
            <SkipForward className="h-4 w-4" />
          </Button>
          <span className="text-sm text-zinc-400 ml-2">0:00 / 2:45</span>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Volume2 className="h-4 w-4 text-zinc-400" />
            <Slider defaultValue={[75]} max={100} className="w-24" />
          </div>
          <Button size="icon" variant="ghost" className="text-zinc-400 hover:text-white">
            <Maximize className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
