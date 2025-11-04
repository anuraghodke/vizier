import { Card } from './ui/card';
import { Image as ImageIcon } from 'lucide-react';

export function PreviewCanvas() {
  return (
    <Card className="flex-1 bg-white border border-zinc-200 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 rounded-lg bg-zinc-100 flex items-center justify-center mx-auto mb-3">
          <ImageIcon className="h-8 w-8 text-zinc-400" />
        </div>
        <p className="text-sm text-zinc-500">Preview will appear here</p>
      </div>
    </Card>
  );
}
