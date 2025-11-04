import { Upload, Image as ImageIcon, X } from 'lucide-react';
import { Card } from './ui/card';
import { useRef } from 'react';

interface UploadSectionProps {
  frame1: File | null;
  frame2: File | null;
  onFrame1Change: (file: File | null) => void;
  onFrame2Change: (file: File | null) => void;
  disabled?: boolean;
}

export function UploadSection({
  frame1,
  frame2,
  onFrame1Change,
  onFrame2Change,
  disabled
}: UploadSectionProps) {
  const frame1Input = useRef<HTMLInputElement>(null);
  const frame2Input = useRef<HTMLInputElement>(null);

  const handleFileChange = (
    file: File | null,
    onChange: (file: File | null) => void
  ) => {
    if (file && file.type === 'image/png') {
      onChange(file);
    }
  };

  const getPreviewUrl = (file: File | null) => {
    return file ? URL.createObjectURL(file) : null;
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Keyframe 1 */}
      <Card
        className={`p-6 border-2 border-dashed bg-white hover:border-purple-200 transition-colors ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        } ${frame1 ? 'border-blue-300' : 'border-blue-200'}`}
        onClick={() => !disabled && frame1Input.current?.click()}
      >
        <input
          ref={frame1Input}
          type="file"
          accept="image/png"
          className="hidden"
          onChange={(e) => handleFileChange(e.target.files?.[0] || null, onFrame1Change)}
          disabled={disabled}
        />

        {frame1 ? (
          <div className="relative">
            <img
              src={getPreviewUrl(frame1) || ''}
              alt="Keyframe 1"
              className="w-full h-32 object-contain rounded-lg"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFrame1Change(null);
              }}
              className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
            >
              <X className="h-4 w-4" />
            </button>
            <div className="mt-2 text-center">
              <p className="text-xs text-zinc-600 font-medium">Keyframe 1</p>
              <p className="text-xs text-zinc-400">{frame1.name}</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <Upload className="h-5 w-5 text-blue-500" />
            </div>
            <div className="text-center">
              <p className="text-sm text-zinc-900">Keyframe 1</p>
              <p className="text-xs text-zinc-500 mt-1">Click to upload first image</p>
              <p className="text-xs text-zinc-400 mt-1">PNG only</p>
            </div>
          </div>
        )}
      </Card>

      {/* Keyframe 2 */}
      <Card
        className={`p-6 border-2 border-dashed bg-white hover:border-purple-200 transition-colors ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        } ${frame2 ? 'border-blue-300' : 'border-blue-200'}`}
        onClick={() => !disabled && frame2Input.current?.click()}
      >
        <input
          ref={frame2Input}
          type="file"
          accept="image/png"
          className="hidden"
          onChange={(e) => handleFileChange(e.target.files?.[0] || null, onFrame2Change)}
          disabled={disabled}
        />

        {frame2 ? (
          <div className="relative">
            <img
              src={getPreviewUrl(frame2) || ''}
              alt="Keyframe 2"
              className="w-full h-32 object-contain rounded-lg"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFrame2Change(null);
              }}
              className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
            >
              <X className="h-4 w-4" />
            </button>
            <div className="mt-2 text-center">
              <p className="text-xs text-zinc-600 font-medium">Keyframe 2</p>
              <p className="text-xs text-zinc-400">{frame2.name}</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <Upload className="h-5 w-5 text-blue-500" />
            </div>
            <div className="text-center">
              <p className="text-sm text-zinc-900">Keyframe 2</p>
              <p className="text-xs text-zinc-500 mt-1">Click to upload second image</p>
              <p className="text-xs text-zinc-400 mt-1">PNG only</p>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
