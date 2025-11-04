import { Upload, Image as ImageIcon } from 'lucide-react';
import { Card } from './ui/card';

export function UploadSection() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Keyframe 1 */}
      <Card className="p-6 border-2 border-dashed border-blue-200 bg-white hover:border-purple-200 transition-colors cursor-pointer">
        <div className="flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <Upload className="h-5 w-5 text-blue-500" />
          </div>
          <div className="text-center">
            <p className="text-sm text-zinc-900">Keyframe 1</p>
            <p className="text-xs text-zinc-500 mt-1">Click to upload first image</p>
          </div>
        </div>
      </Card>
      
      {/* Keyframe 2 */}
      <Card className="p-6 border-2 border-dashed border-blue-200 bg-white hover:border-purple-200 transition-colors cursor-pointer">
        <div className="flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <Upload className="h-5 w-5 text-blue-500" />
          </div>
          <div className="text-center">
            <p className="text-sm text-zinc-900">Keyframe 2</p>
            <p className="text-xs text-zinc-500 mt-1">Click to upload second image</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
