import { Film, Image, Music, FileText, Plus } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Button } from './ui/button';

const mockMedia = [
  { id: 1, name: 'intro-clip.mp4', type: 'video', duration: '0:15' },
  { id: 2, name: 'main-scene.mp4', type: 'video', duration: '1:24' },
  { id: 3, name: 'outro.mp4', type: 'video', duration: '0:08' },
];

const mockImages = [
  { id: 1, name: 'logo.png', type: 'image' },
  { id: 2, name: 'overlay.png', type: 'image' },
  { id: 3, name: 'background.jpg', type: 'image' },
];

const mockAudio = [
  { id: 1, name: 'background-music.mp3', type: 'audio', duration: '2:45' },
  { id: 2, name: 'sound-effect.mp3', type: 'audio', duration: '0:03' },
];

export function FilePanel() {
  return (
    <div className="w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="p-4 border-b border-zinc-800">
        <Button className="w-full" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Add Media
        </Button>
      </div>
      
      <Tabs defaultValue="media" className="flex-1 flex flex-col">
        <TabsList className="w-full grid grid-cols-3 bg-zinc-900 border-b border-zinc-800">
          <TabsTrigger value="media">Media</TabsTrigger>
          <TabsTrigger value="images">Images</TabsTrigger>
          <TabsTrigger value="audio">Audio</TabsTrigger>
        </TabsList>
        
        <TabsContent value="media" className="flex-1 m-0">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {mockMedia.map((item) => (
                <div
                  key={item.id}
                  className="p-3 bg-zinc-800 rounded hover:bg-zinc-750 cursor-pointer transition-colors"
                  draggable
                >
                  <div className="flex items-start gap-2">
                    <Film className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-white truncate">{item.name}</div>
                      <div className="text-xs text-zinc-400">{item.duration}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
        
        <TabsContent value="images" className="flex-1 m-0">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {mockImages.map((item) => (
                <div
                  key={item.id}
                  className="p-3 bg-zinc-800 rounded hover:bg-zinc-750 cursor-pointer transition-colors"
                  draggable
                >
                  <div className="flex items-start gap-2">
                    <Image className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-white truncate">{item.name}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
        
        <TabsContent value="audio" className="flex-1 m-0">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              {mockAudio.map((item) => (
                <div
                  key={item.id}
                  className="p-3 bg-zinc-800 rounded hover:bg-zinc-750 cursor-pointer transition-colors"
                  draggable
                >
                  <div className="flex items-start gap-2">
                    <Music className="h-4 w-4 text-purple-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-white truncate">{item.name}</div>
                      <div className="text-xs text-zinc-400">{item.duration}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}
