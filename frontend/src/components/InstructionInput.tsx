import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { Wand2 } from 'lucide-react';

interface InstructionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function InstructionInput({ value, onChange, disabled }: InstructionInputProps) {
  return (
    <Card className="p-4 bg-white border border-zinc-200">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
          <Wand2 className="h-4 w-4 text-purple-600" />
        </div>
        <div>
          <h3 className="text-sm font-medium text-zinc-900">Animation Instruction</h3>
          <p className="text-xs text-zinc-500">Describe the motion you want</p>
        </div>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder='e.g., "create 8 bouncy frames with smooth ease-in-out motion"'
        className="min-h-[80px] resize-none text-sm"
        maxLength={500}
      />

      <div className="mt-2 flex justify-between items-center text-xs text-zinc-500">
        <span>Minimum 5 characters</span>
        <span>{value.length}/500</span>
      </div>
    </Card>
  );
}
