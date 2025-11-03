import { Undo2, Redo2, Save, Download, Upload } from 'lucide-react';
import { Button } from './ui/button';

export function Toolbar() {
  return (
    <div className="h-14 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between px-4">
      <div className="flex items-center gap-2">
        <h1 className="text-white mr-4">Video Editor</h1>
        <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white">
          <Undo2 className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white">
          <Redo2 className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
          <Upload className="h-4 w-4 mr-2" />
          Import
        </Button>
        <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
          <Save className="h-4 w-4 mr-2" />
          Save
        </Button>
        <Button variant="default" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
      </div>
    </div>
  );
}
