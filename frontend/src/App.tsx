import { UploadSection } from './components/UploadSection';
import { PreviewCanvas } from './components/PreviewCanvas';
import { InterpolationTimeline } from './components/InterpolationTimeline';
import { Header } from './components/Header';

export default function App() {
  return (
    <div className="h-screen flex flex-col bg-zinc-50">
      <Header />
      
      <div className="flex-1 flex flex-col overflow-hidden p-6 gap-6">
        {/* Upload Section */}
        <UploadSection />
        
        {/* Preview Canvas */}
        <PreviewCanvas />
        
        {/* Timeline */}
        <InterpolationTimeline />
      </div>
    </div>
  );
}
