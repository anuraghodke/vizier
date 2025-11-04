import { Button } from './ui/button';

export function Header() {
  return (
    <div className="h-16 bg-white border-b border-zinc-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        {/* Logo placeholder */}
        <div className="w-10 h-10 rounded-lg bg-blue-200 flex items-center justify-center">
          <span className="text-blue-700 text-sm">V</span>
        </div>
        <h1 className="text-zinc-900">Vizier</h1>
      </div>
      
      <Button className="bg-purple-200 hover:bg-purple-300 text-purple-800">
        Generate Frames
      </Button>
    </div>
  );
}
