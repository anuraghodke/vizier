import { Layers, Film, Music, Type, Scissors, Plus } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { Button } from './ui/button';

const tracks = [
  { id: 1, name: 'Video 1', type: 'video', clips: [{ start: 0, duration: 15, color: 'bg-blue-600' }, { start: 20, duration: 24, color: 'bg-blue-600' }] },
  { id: 2, name: 'Video 2', type: 'video', clips: [{ start: 40, duration: 8, color: 'bg-blue-500' }] },
  { id: 3, name: 'Audio', type: 'audio', clips: [{ start: 0, duration: 45, color: 'bg-purple-600' }] },
  { id: 4, name: 'Text', type: 'text', clips: [{ start: 5, duration: 10, color: 'bg-green-600' }] },
];

export function Timeline() {
  return (
    <div className="h-64 bg-zinc-900 border-t border-zinc-800 flex flex-col">
      {/* Timeline Header */}
      <div className="h-12 border-b border-zinc-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-zinc-400" />
          <span className="text-sm">Timeline</span>
        </div>
        <div className="flex items-center gap-1">
          <Button size="icon" variant="ghost" className="h-8 w-8 text-zinc-400 hover:text-white">
            <Plus className="h-4 w-4" />
          </Button>
          <Button size="icon" variant="ghost" className="h-8 w-8 text-zinc-400 hover:text-white">
            <Scissors className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Timeline Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Labels */}
        <div className="w-32 bg-zinc-900 border-r border-zinc-800">
          <ScrollArea className="h-full">
            <div className="py-1">
              {tracks.map((track) => (
                <div key={track.id} className="h-12 px-3 flex items-center gap-2 border-b border-zinc-800">
                  {track.type === 'video' && <Film className="h-3 w-3 text-blue-400" />}
                  {track.type === 'audio' && <Music className="h-3 w-3 text-purple-400" />}
                  {track.type === 'text' && <Type className="h-3 w-3 text-green-400" />}
                  <span className="text-xs text-zinc-400 truncate">{track.name}</span>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
        
        {/* Timeline Ruler and Tracks */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Ruler */}
          <div className="h-8 bg-zinc-950 border-b border-zinc-800 relative">
            <div className="absolute inset-0 flex">
              {Array.from({ length: 60 }).map((_, i) => (
                <div key={i} className="flex-shrink-0 w-12 border-l border-zinc-700 relative">
                  {i % 5 === 0 && (
                    <span className="absolute top-1 left-1 text-xs text-zinc-500">
                      {Math.floor(i / 5)}s
                    </span>
                  )}
                </div>
              ))}
            </div>
            {/* Playhead */}
            <div className="absolute top-0 left-0 w-0.5 h-full bg-red-500" style={{ left: '120px' }}>
              <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rounded-sm" />
            </div>
          </div>
          
          {/* Tracks */}
          <ScrollArea className="flex-1">
            <div className="relative" style={{ width: '720px' }}>
              {tracks.map((track) => (
                <div key={track.id} className="h-12 border-b border-zinc-800 relative">
                  {track.clips.map((clip, idx) => (
                    <div
                      key={idx}
                      className={`absolute top-1 bottom-1 ${clip.color} rounded cursor-pointer hover:opacity-80 transition-opacity flex items-center px-2`}
                      style={{
                        left: `${clip.start * 12}px`,
                        width: `${clip.duration * 12}px`,
                      }}
                    >
                      <span className="text-xs text-white truncate">Clip {idx + 1}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>
      
      {/* Zoom Controls */}
      <div className="h-10 border-t border-zinc-800 flex items-center justify-center gap-2 px-4">
        <Button variant="ghost" size="sm" className="text-xs text-zinc-400 hover:text-white">
          −
        </Button>
        <div className="w-24 h-1 bg-zinc-700 rounded-full">
          <div className="w-1/2 h-full bg-zinc-500 rounded-full" />
        </div>
        <Button variant="ghost" size="sm" className="text-xs text-zinc-400 hover:text-white">
          +
        </Button>
      </div>
    </div>
  );
}
