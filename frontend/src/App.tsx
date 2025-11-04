import { useState } from 'react';
import { UploadSection } from './components/UploadSection';
import { PreviewCanvas } from './components/PreviewCanvas';
import { InterpolationTimeline } from './components/InterpolationTimeline';
import { Header } from './components/Header';
import { InstructionInput } from './components/InstructionInput';
import { Button } from './components/ui/button';
import { Alert, AlertDescription } from './components/ui/alert';
import { Progress } from './components/ui/progress';
import { Loader2, Play, Download, AlertCircle } from 'lucide-react';
import { generateAnimation, downloadFrames } from './utils/api';
import { useJobStatus } from './hooks/useJobStatus';

export default function App() {
  // Upload state
  const [frame1, setFrame1] = useState<File | null>(null);
  const [frame2, setFrame2] = useState<File | null>(null);
  const [instruction, setInstruction] = useState('');

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Job polling
  const { jobStatus, isPolling, startPolling } = useJobStatus();

  // Validation
  const canGenerate = frame1 && frame2 && instruction.length >= 5 && !isGenerating;

  const handleGenerate = async () => {
    if (!frame1 || !frame2) return;

    try {
      setIsGenerating(true);
      setError(null);

      const response = await generateAnimation(frame1, frame2, instruction);
      startPolling(response.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start generation');
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (jobStatus?.job_id) {
      downloadFrames(jobStatus.job_id);
    }
  };

  const handleReset = () => {
    setFrame1(null);
    setFrame2(null);
    setInstruction('');
    setIsGenerating(false);
    setError(null);
  };

  return (
    <div className="h-screen flex flex-col bg-zinc-50">
      <Header />

      <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">
        {/* Upload Section */}
        <UploadSection
          frame1={frame1}
          frame2={frame2}
          onFrame1Change={setFrame1}
          onFrame2Change={setFrame2}
          disabled={isGenerating || isPolling}
        />

        {/* Instruction Input */}
        <InstructionInput
          value={instruction}
          onChange={setInstruction}
          disabled={isGenerating || isPolling}
        />

        {/* Generate Button */}
        <div className="flex gap-3">
          <Button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="flex-1"
            size="lg"
          >
            {isGenerating || isPolling ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {jobStatus?.stage || 'Processing...'}
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Generate Animation
              </>
            )}
          </Button>

          {jobStatus?.status === 'complete' && (
            <Button
              onClick={handleDownload}
              variant="outline"
              size="lg"
            >
              <Download className="h-4 w-4 mr-2" />
              Download ZIP
            </Button>
          )}

          {(isGenerating || isPolling || jobStatus) && (
            <Button onClick={handleReset} variant="outline" size="lg">
              Reset
            </Button>
          )}
        </div>

        {/* Progress Bar */}
        {(isGenerating || isPolling) && jobStatus && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-600">
                {jobStatus.stage || 'Processing...'}
              </span>
              <span className="text-zinc-600">{jobStatus.progress}%</span>
            </div>
            <Progress value={jobStatus.progress} className="h-2" />
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Preview Canvas */}
        <PreviewCanvas />

        {/* Timeline */}
        <InterpolationTimeline />
      </div>
    </div>
  );
}
